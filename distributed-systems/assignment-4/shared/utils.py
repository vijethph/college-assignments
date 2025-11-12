"""Shared Utility Functions."""

import time
from functools import wraps
from typing import Any, Callable

import requests

from shared.logging_config import get_logger


logger = get_logger()


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry a function on failure with exponential backoff.

    :param max_retries: Maximum number of retry attempts
    :type max_retries: int
    :param delay: Initial delay between retries in seconds
    :type delay: float
    :return: Decorated function
    :rtype: Callable
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Exception = Exception("Max retries exceeded")

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            "request_failed_retrying",
                            attempt=attempt + 1,
                            max_retries=max_retries,
                            error=str(e),
                        )
                        time.sleep(delay * (2**attempt))
                    else:
                        logger.error(
                            "request_failed_max_retries",
                            max_retries=max_retries,
                            error=str(e),
                        )
            raise last_exception

        return wrapper

    return decorator


def log_request(service_name: str, endpoint: str, method: str = "GET"):
    """
    Decorator to log inter-service HTTP requests.

    :param service_name: Name of the target service
    :type service_name: str
    :param endpoint: API endpoint being called
    :type endpoint: str
    :param method: HTTP method
    :type method: str
    :return: Decorated function
    :rtype: Callable
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.info(
                    "inter_service_call",
                    target_service=service_name,
                    endpoint=endpoint,
                    method=method,
                    duration_ms=round(elapsed * 1000, 2),
                    status="success",
                )
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    "inter_service_call_failed",
                    target_service=service_name,
                    endpoint=endpoint,
                    method=method,
                    duration_ms=round(elapsed * 1000, 2),
                    error=str(e),
                )
                raise

        return wrapper

    return decorator
