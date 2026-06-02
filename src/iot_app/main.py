import os
from datetime import datetime, timezone
from enum import Enum
from http import HTTPStatus
from typing import Annotated, Dict, List, Literal, Optional, Union
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

SERVICE_NAME = os.getenv("SERVICE_NAME", "iot-ingestion")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "0.4.0")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "local-dev-token")

STATIC_EVENT_ID = "0196fb3d-4ad7-7d1e-9f49-5d5148d2b101"

app = FastAPI(
    title="FIT4110 Lab 04 - IoT Ingestion Service",
    version=SERVICE_VERSION,
    description="Dockerized IoT Ingestion API that runs the Lab 03 contract on a real container.",
)


class ProblemDetails(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    title: str
    status: int = Field(..., ge=400, le=599)
    detail: Optional[str] = None
    instance: Optional[str] = None
    errors: List[Dict[str, str]] = Field(default_factory=list)


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"]
    service: str
    time: str


class NumericUnit(str, Enum):
    CELSIUS = "CELSIUS"
    PERCENT = "PERCENT"
    WATT = "WATT"
    AQI = "AQI"


class NumericTelemetryMeasurement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sensorType: Literal["TEMPERATURE", "HUMIDITY", "POWER", "AIR_QUALITY"]
    value: float = Field(..., ge=-1000, le=100000)
    unit: NumericUnit


class BooleanTelemetryMeasurement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sensorType: Literal["MOTION"]
    detected: bool
    unit: Literal["BOOLEAN"]


TelemetryMeasurement = Annotated[
    Union[NumericTelemetryMeasurement, BooleanTelemetryMeasurement],
    Field(discriminator="sensorType"),
]


class IngestTelemetryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    deviceId: str = Field(..., pattern=r"^IOT-DEV-[0-9]{3}$")
    zoneId: str = Field(..., pattern=r"^ZONE-[A-Z][0-9]$")
    measurement: TelemetryMeasurement
    timestamp: datetime
    metadata: Dict[str, str]


class TelemetryAccepted(BaseModel):
    model_config = ConfigDict(extra="forbid")

    eventId: str
    status: Literal["ACCEPTED"]
    publishedEvents: List[str]
    acceptedAt: str


class TelemetryAudit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    eventId: str
    deviceId: str
    zoneId: str
    measurement: Dict
    timestamp: str
    acceptedAt: str
    publishedEvents: List[str]


class DeviceStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    deviceId: str
    zoneId: str
    status: Literal["ONLINE", "OFFLINE", "ERROR", "MAINTENANCE"]
    lastSeenAt: str
    batteryLevel: int = Field(..., ge=0, le=100)
    firmwareVersion: str




EVENTS: Dict[str, Dict] = {
    STATIC_EVENT_ID: {
        "eventId": STATIC_EVENT_ID,
        "deviceId": "IOT-DEV-001",
        "zoneId": "ZONE-A1",
        "measurement": {
            "sensorType": "TEMPERATURE",
            "value": 31.5,
            "unit": "CELSIUS",
        },
        "timestamp": "2026-05-19T02:59:58Z",
        "acceptedAt": "2026-05-19T03:00:00Z",
        "publishedEvents": ["sensor.reading.created", "telemetry.ingested"],
    }
}

DEVICES: Dict[str, Dict] = {
    "IOT-DEV-001": {
        "deviceId": "IOT-DEV-001",
        "zoneId": "ZONE-A1",
        "status": "ONLINE",
        "lastSeenAt": "2026-05-19T03:00:00Z",
        "batteryLevel": 88,
        "firmwareVersion": "1.4.2",
    }
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def build_problem(
    *,
    status_code: int,
    title: str,
    detail: str,
    instance: Optional[str] = None,
    problem_type: str = "about:blank",
    errors: Optional[List[Dict[str, str]]] = None,
) -> Dict:
    return {
        "type": problem_type,
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": instance,
        "errors": errors or [],
    }


def reason_phrase(status_code: int) -> str:
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return "HTTP Error"


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict):
        problem = exc.detail
    else:
        problem = build_problem(
            status_code=exc.status_code,
            title=reason_phrase(exc.status_code),
            detail=str(exc.detail),
            instance=str(request.url.path),
        )

    problem.setdefault("type", "about:blank")
    problem.setdefault("title", reason_phrase(exc.status_code))
    problem.setdefault("status", exc.status_code)
    problem.setdefault("detail", "Request failed")
    problem.setdefault("instance", str(request.url.path))
    problem.setdefault("errors", [])

    return JSONResponse(
        status_code=exc.status_code,
        content=problem,
        media_type="application/problem+json",
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = []
    for err in exc.errors():
        field = ".".join(str(part) for part in err.get("loc", []) if part != "body")
        errors.append(
            {
                "field": field or "request",
                "code": err.get("type", "VALIDATION_ERROR"),
                "message": err.get("msg", "Request validation error"),
            }
        )

    detail = errors[0]["message"] if errors else "Payload does not match the OpenAPI schema."
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=build_problem(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Request is not valid",
            detail=detail,
            instance=str(request.url.path),
            problem_type="https://campus.local/errors/validation",
            errors=errors,
        ),
        media_type="application/problem+json",
    )


def verify_bearer_token(authorization: Optional[str] = Header(default=None)) -> None:
    if authorization != f"Bearer {AUTH_TOKEN}":
        detail = "Missing Bearer token." if not authorization else "Invalid Bearer token."
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=build_problem(
                status_code=status.HTTP_401_UNAUTHORIZED,
                title="Authentication required",
                detail=detail,
                instance="",
                problem_type="https://campus.local/errors/unauthorized",
            ),
        )


def require_idempotency_key(idempotency_key: Optional[str] = Header(default=None)) -> str:
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=build_problem(
                status_code=status.HTTP_400_BAD_REQUEST,
                title="Request is not valid",
                detail="Idempotency-Key header is required.",
                problem_type="https://campus.local/errors/validation",
            ),
        )
    return idempotency_key


def published_events_for(payload: IngestTelemetryRequest) -> List[str]:
    published = ["sensor.reading.created", "telemetry.ingested"]
    if (
        isinstance(payload.measurement, NumericTelemetryMeasurement)
        and payload.measurement.sensorType == "AIR_QUALITY"
        and payload.measurement.value >= 100000
    ):
        published.insert(1, "sensor.threshold.exceeded")
    return published


def store_event(payload: IngestTelemetryRequest, accepted_at: str) -> str:
    event_id = str(uuid4())
    EVENTS[event_id] = {
        "eventId": event_id,
        "deviceId": payload.deviceId,
        "zoneId": payload.zoneId,
        "measurement": payload.measurement.model_dump(mode="json"),
        "timestamp": payload.timestamp.isoformat().replace("+00:00", "Z"),
        "acceptedAt": accepted_at,
        "publishedEvents": published_events_for(payload),
    }
    DEVICES[payload.deviceId] = {
        "deviceId": payload.deviceId,
        "zoneId": payload.zoneId,
        "status": "ONLINE",
        "lastSeenAt": accepted_at,
        "batteryLevel": 100,
        "firmwareVersion": payload.metadata.get("firmwareVersion", "unknown"),
    }
    return event_id


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service=SERVICE_NAME, time=utc_now())


@app.post(
    "/events/sensor",
    response_model=TelemetryAccepted,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(verify_bearer_token), Depends(require_idempotency_key)],
    responses={400: {"model": ProblemDetails}, 401: {"model": ProblemDetails}, 422: {"model": ProblemDetails}},
)
def ingest_sensor_event(
    payload: IngestTelemetryRequest,
    response: Response,
    x_correlation_id: Optional[str] = Header(default=None),
) -> TelemetryAccepted:
    accepted_at = utc_now()
    event_id = store_event(payload, accepted_at)
    if x_correlation_id:
        response.headers["X-Correlation-Id"] = x_correlation_id
    return TelemetryAccepted(
        eventId=event_id,
        status="ACCEPTED",
        publishedEvents=EVENTS[event_id]["publishedEvents"],
        acceptedAt=accepted_at,
    )


@app.post(
    "/telemetry",
    response_model=TelemetryAccepted,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(verify_bearer_token), Depends(require_idempotency_key)],
    responses={400: {"model": ProblemDetails}, 401: {"model": ProblemDetails}, 422: {"model": ProblemDetails}},
)
def ingest_telemetry(
    payload: IngestTelemetryRequest,
    response: Response,
    x_correlation_id: Optional[str] = Header(default=None),
) -> TelemetryAccepted:
    return ingest_sensor_event(payload, response, x_correlation_id)


@app.get(
    "/telemetry/{eventId}",
    response_model=TelemetryAudit,
    dependencies=[Depends(verify_bearer_token)],
    responses={401: {"model": ProblemDetails}, 404: {"model": ProblemDetails}},
)
def get_telemetry_audit(eventId: str) -> Dict:
    if eventId not in EVENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=build_problem(
                status_code=status.HTTP_404_NOT_FOUND,
                title="Resource not found",
                detail="Event id was not found.",
                instance=f"/telemetry/{eventId}",
                problem_type="https://campus.local/errors/not-found",
            ),
        )
    return EVENTS[eventId]


@app.get(
    "/devices/{deviceId}",
    response_model=DeviceStatus,
    dependencies=[Depends(verify_bearer_token)],
    responses={401: {"model": ProblemDetails}, 404: {"model": ProblemDetails}},
)
def get_device_status(deviceId: str) -> Dict:
    if deviceId not in DEVICES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=build_problem(
                status_code=status.HTTP_404_NOT_FOUND,
                title="Resource not found",
                detail="Device id was not found.",
                instance=f"/devices/{deviceId}",
                problem_type="https://campus.local/errors/not-found",
            ),
        )
    return DEVICES[deviceId]
