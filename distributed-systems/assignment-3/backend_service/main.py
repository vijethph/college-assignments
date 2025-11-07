import random
import time
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()

app = FastAPI()

API_DATA_ENDPOINT = "/api/data"


class FailureConfig(BaseModel):
    failure_rate: float = 0.0
    status_code: int = 500


class LatencyConfig(BaseModel):
    delay_ms: int = 0
    delay_rate: float = 0.0


failure_config = FailureConfig()
latency_config = LatencyConfig()


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/config/failure")
async def configure_failure(config: FailureConfig):
    global failure_config
    failure_config = config
    logger.info(
        "failure_config_updated",
        failure_rate=config.failure_rate,
        status_code=config.status_code,
    )
    return {"status": "success", "config": config.dict()}


@app.post("/config/latency")
async def configure_latency(config: LatencyConfig):
    global latency_config
    latency_config = config
    logger.info(
        "latency_config_updated", delay_ms=config.delay_ms, delay_rate=config.delay_rate
    )
    return {"status": "success", "config": config.dict()}


@app.get("/config")
async def get_config():
    return {"failure": failure_config.dict(), "latency": latency_config.dict()}


@app.get(API_DATA_ENDPOINT)
async def get_data():
    if random.random() < failure_config.failure_rate:
        logger.error(
            "simulated_failure",
            endpoint=API_DATA_ENDPOINT,
            status_code=failure_config.status_code,
        )
        raise HTTPException(
            status_code=failure_config.status_code, detail="Simulated failure"
        )

    if random.random() < latency_config.delay_rate:
        delay_seconds = latency_config.delay_ms / 1000.0
        logger.warning(
            "simulated_delay", endpoint=API_DATA_ENDPOINT, delay_seconds=delay_seconds
        )
        await asyncio.sleep(delay_seconds)

    data = {
        "message": "Data retrieved successfully",
        "timestamp": time.time(),
        "data": {"value": random.randint(1, 100)},
    }
    logger.info("request_successful", endpoint=API_DATA_ENDPOINT)
    return data


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
