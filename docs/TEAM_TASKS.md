# Team Tasks

This repository is completed for the IoT Ingestion team using the Lab 03 contract.

## Completed Items

- [x] Copy the Lab 03 IoT OpenAPI contract into `contracts/`.
- [x] Implement `GET /health`.
- [x] Implement the Lab 03 IoT endpoints used by the Postman collection.
- [x] Update `Dockerfile`.
- [x] Add `.dockerignore`.
- [x] Add `.env.example`.
- [x] Add `RUN_LOCAL.md`.
- [x] Build the Docker image.
- [x] Run the container.
- [x] Run the Lab 03 Postman/Newman tests against the container.
- [x] Export Newman reports.
- [x] Record Docker and health evidence.
- [x] Create image tag `fit4110/iot-ingestion:v0.1.0-team-iot`.

## Implemented Service Scope

| Service | Scope |
|---|---|
| IoT Ingestion | Telemetry/event ingestion, auth token checks, health endpoint, device status lookup, audit lookup, boundary validation |

## Next Step For Lab 05

Move from one standalone container to Docker Compose with dependent services such as Core Business, Analytics, or a message broker mock.
