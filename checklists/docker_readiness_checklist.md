# Docker Readiness Checklist

## Dockerfile

- [x] Base image is reasonable: `python:3.11-slim`.
- [x] Uses `WORKDIR /app`.
- [x] Copies dependency file before source to use Docker cache.
- [x] Uses `EXPOSE 8000`.
- [x] Uses `CMD` to run Uvicorn.
- [x] Has `HEALTHCHECK` calling `GET /health`.
- [x] Runs as non-root user `appuser`.
- [x] Does not bake a real secret into the image; `AUTH_TOKEN` comes from `.env.example` or runtime env.

## Runtime

- [x] Image builds: `fit4110/iot-ingestion:lab04`.
- [x] Container runs as `fit4110-iot-lab04`.
- [x] Port mapping works: `8000:8000`.
- [x] `/health` returns `200`.
- [x] Container health status is `healthy`.
- [x] Runtime config is passed through environment variables.

## Testing

- [x] Reuses the Lab 03 IoT Ingestion contract flow.
- [x] Newman report is generated in `reports/`.
- [x] Functional tests pass.
- [x] Auth tests pass on the real container.
- [x] Negative tests pass on the real container.
- [x] Boundary tests pass.
- [x] Error responses follow Problem Details shape.

## Evidence

- [x] Docker build completed.
- [x] Docker run completed.
- [x] `curl /health` returned `status: ok`.
- [x] Newman HTML/XML reports generated.
- [x] Image tag created: `fit4110/iot-ingestion:v0.1.0-team-iot`.
