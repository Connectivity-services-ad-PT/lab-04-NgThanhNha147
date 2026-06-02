# FIT4110 Lab 04 - Docker Packaging

Service: `iot-ingestion`

This lab packages the real Lab 03 IoT Ingestion contract into a Docker container and reruns Newman against the container.

Lab 03 source used for continuity:

```text
../lab-03-api-contract-testing-NgThanhNha147/
```

## Lab 03 To Lab 04 Flow

Lab 03:

```text
OpenAPI Contract -> Prism Mock Server -> Postman Tests -> Newman Report
```

Lab 04:

```text
OpenAPI Contract
-> Real FastAPI service
-> Dockerfile
-> Docker image
-> Docker container
-> Newman tests against the container
-> Evidence reports
```

## Implemented Endpoints

The Dockerized service follows the Lab 03 IoT Ingestion contract:

- `GET /health`
- `POST /events/sensor`
- `POST /telemetry`
- `GET /telemetry/{eventId}`
- `GET /devices/{deviceId}`

The main payload shape is:

```json
{
  "deviceId": "IOT-DEV-001",
  "zoneId": "ZONE-A1",
  "measurement": {
    "sensorType": "TEMPERATURE",
    "value": 31.5,
    "unit": "CELSIUS"
  },
  "timestamp": "2026-05-19T02:59:58Z",
  "metadata": {}
}
```

Boundary used by the Lab 03 contract:

```text
numeric telemetry value: -1000 to 100000
```

## Repository Structure

```text
lab-04-NgThanhNha147/
|-- Dockerfile
|-- .dockerignore
|-- .env.example
|-- .spectral.yaml
|-- RUN_LOCAL.md
|-- Makefile
|-- package.json
|-- package-lock.json
|-- requirements.txt
|-- src/iot_app/main.py
|-- contracts/iot-ingestion.openapi.yaml
|-- postman/
|-- reports/
|-- scripts/
|-- docs/
`-- checklists/
```

## Quick Start

Install Node test tools:

```bash
npm install
```

Lint the OpenAPI contract:

```bash
npm run lint:openapi
```

Build the image:

```bash
docker build -t fit4110/iot-ingestion:lab04 .
```

Run the container:

```bash
docker run --rm \
  --name fit4110-iot-lab04 \
  -p 8000:8000 \
  --env-file .env.example \
  fit4110/iot-ingestion:lab04
```

Check health:

```bash
curl http://localhost:8000/health
```

Run Newman against the container:

```bash
npm run test:local
```

## Docker Requirements Covered

- Multi-stage Dockerfile.
- `.dockerignore` reduces build context.
- Runtime config is passed through `.env.example`.
- The image runs as non-root user `appuser`.
- `HEALTHCHECK` calls `GET /health`.
- No real secret is committed; `AUTH_TOKEN=local-dev-token` is a local lab placeholder.
- Newman verifies functional, auth, negative, boundary, consumer smoke, and Problem Details behavior.

## Evidence

Generated evidence:

```text
reports/newman-lab04-local.xml
reports/newman-lab04-local.html
reports/docker-evidence.md
```

Verified local result:

```text
Requests: 13 executed, 0 failed
Assertions: 23 executed, 0 failed
Container: running, healthy, user appuser
Image tag: fit4110/iot-ingestion:v0.1.0-team-iot
```
