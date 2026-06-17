from __future__ import annotations

from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, HTTPException

from app.inference import model_service
from app.monitoring import (
    PREDICTION_ERRORS,
    PREDICTION_LATENCY,
    PREDICTION_REQUESTS,
    metrics_response,
    monitoring_dashboard_response,
    monitoring_snapshot,
    record_prediction,
)
from app.schemas import HealthResponse, PredictionRequest, PredictionResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_service.load()
    yield


app = FastAPI(
    title="Network Intrusion Detection System",
    description="Binary intrusion detection API trained on UNSW-NB15.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(**model_service.health())


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest) -> PredictionResponse:
    PREDICTION_REQUESTS.inc()
    start = perf_counter()
    try:
        result = model_service.predict(payload)
    except Exception as exc:
        latency = perf_counter() - start
        PREDICTION_LATENCY.observe(latency)
        PREDICTION_ERRORS.inc()
        record_prediction(latency, error=True)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    latency = perf_counter() - start
    PREDICTION_LATENCY.observe(latency)
    record_prediction(latency, result=result)

    return PredictionResponse(**result)


@app.get("/metrics")
def metrics():
    return metrics_response()


@app.get("/monitoring", include_in_schema=False)
def monitoring():
    return monitoring_dashboard_response(model_service.health())


@app.get("/monitoring/snapshot", include_in_schema=False)
def monitoring_snapshot_json():
    return monitoring_snapshot()
