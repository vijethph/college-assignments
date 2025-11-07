import time
import random
import httpx
from fastapi import FastAPI
import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = structlog.get_logger()

app = FastAPI()

BACKEND_URL = "http://backend-service:8000"


class CircuitBreakerOpen(Exception):
    pass


class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=30, half_open_max_calls=1):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"
        self.half_open_calls = 0

    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = "HALF-OPEN"
                self.half_open_calls = 0
                logger.info(
                    "circuit_breaker_half_open",
                    message="Circuit breaker entering HALF-OPEN state",
                )
            else:
                logger.error(
                    "circuit_breaker_open",
                    message="Circuit breaker is OPEN. Failing fast.",
                    failure_count=self.failure_count,
                )
                raise CircuitBreakerOpen("Circuit breaker is OPEN")

        if self.state == "HALF-OPEN":
            if self.half_open_calls >= self.half_open_max_calls:
                logger.error(
                    "circuit_breaker_half_open_limit",
                    message="Circuit breaker HALF-OPEN call limit reached",
                )
                raise CircuitBreakerOpen("Circuit breaker HALF-OPEN call limit reached")
            self.half_open_calls += 1

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e

    def on_success(self):
        if self.state == "HALF-OPEN":
            self.state = "CLOSED"
            self.failure_count = 0
            logger.info(
                "circuit_breaker_closed",
                message="Circuit breaker CLOSING. Service recovered.",
            )
        elif self.state == "CLOSED":
            self.failure_count = 0

    def on_failure(self):
        self.failure_count += 1

        if self.state == "HALF-OPEN":
            self.state = "OPEN"
            self.last_failure_time = time.time()
            logger.error(
                "circuit_breaker_reopened",
                message="Circuit breaker RE-OPENING after failed test call",
                failure_count=self.failure_count,
            )
        elif self.state == "CLOSED":
            logger.warning(
                "circuit_breaker_failure_count",
                message="Backend service failure detected",
                failure_count=self.failure_count,
                threshold=self.failure_threshold,
            )
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                self.last_failure_time = time.time()
                logger.error(
                    "circuit_breaker_opened",
                    message=f"Circuit breaker OPENING. Failing fast for next {self.timeout}s",
                    failure_count=self.failure_count,
                )


circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=30, half_open_max_calls=1)


def is_transient_error(exception):
    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code in [408, 429, 502, 503, 504]
    return isinstance(exception, (httpx.TimeoutException, httpx.ConnectError))


class RetryContext:
    def __init__(self):
        self.attempt = 0


def log_retry_attempt(retry_state):
    exception = retry_state.outcome.exception()
    attempt = retry_state.attempt_number

    if isinstance(exception, (httpx.TimeoutException, httpx.ConnectError)):
        wait_time = 2 ** (attempt - 1) + random.uniform(0, 1)
        logger.warning(
            "retry_attempt",
            message=f"Call failed ({type(exception).__name__}). Retrying in {wait_time:.1f}s",
            error_type=type(exception).__name__,
            attempt=attempt,
            max_attempts=3,
        )


@retry(
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    before_sleep=log_retry_attempt,
    reraise=True,
)
def make_backend_request_with_retry(client, attempt_tracker):
    attempt_tracker.attempt += 1

    response = client.get(f"{BACKEND_URL}/api/data")

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        if is_transient_error(e) and attempt_tracker.attempt < 3:
            wait_time = 2 ** (attempt_tracker.attempt - 1) + random.uniform(0, 1)
            logger.warning(
                "retry_attempt",
                message=f"Call failed (transient error {e.response.status_code}). Retrying in {wait_time:.1f}s",
                status_code=e.response.status_code,
                attempt=attempt_tracker.attempt,
                max_attempts=3,
            )
            time.sleep(wait_time)
            return make_backend_request_with_retry(client, attempt_tracker)
        raise

    if attempt_tracker.attempt > 1:
        logger.info(
            "retry_success",
            message=f"Call successful on retry attempt {attempt_tracker.attempt}",
            attempt=attempt_tracker.attempt,
        )

    return response


def make_backend_request():
    attempt_tracker = RetryContext()
    with httpx.Client(timeout=10.0) as client:
        return make_backend_request_with_retry(client, attempt_tracker)


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Client Service is running"}


@app.get("/fetch-data")
async def fetch_data():
    try:
        response = circuit_breaker.call(make_backend_request)
        logger.info("backend_request_successful", status_code=response.status_code)
        return {"status": "success", "backend_response": response.json()}
    except CircuitBreakerOpen as e:
        logger.error("request_failed_circuit_open", message=str(e))
        return {
            "status": "error",
            "message": "Service temporarily unavailable (circuit breaker open)",
        }
    except httpx.TimeoutException:
        logger.error("backend_request_timeout", backend_url=BACKEND_URL)
        return {"status": "error", "message": "Backend service timeout"}
    except httpx.HTTPStatusError as e:
        logger.error("backend_request_failed", status_code=e.response.status_code)
        return {
            "status": "error",
            "message": f"Backend returned {e.response.status_code}",
        }
    except httpx.RequestError as e:
        logger.error("backend_request_exception", error=str(e))
        return {"status": "error", "message": str(e)}


@app.get("/circuit-status")
async def circuit_status():
    return {
        "state": circuit_breaker.state,
        "failure_count": circuit_breaker.failure_count,
        "failure_threshold": circuit_breaker.failure_threshold,
        "timeout": circuit_breaker.timeout,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9090)
