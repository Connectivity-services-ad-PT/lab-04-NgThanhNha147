# RUN_LOCAL.md - Run Lab 04

This lab packages the Lab 03 IoT Ingestion contract as a real Docker container.

## 1. Install test tools

```bash
npm install
```

## 2. Build the image

```bash
docker build -t fit4110/iot-ingestion:lab04 .
```

Optional submission tag:

```bash
docker tag fit4110/iot-ingestion:lab04 fit4110/iot-ingestion:v0.1.0-team-iot
```

## 3. Run the container

```bash
docker run --rm \
  --name fit4110-iot-lab04 \
  -p 8000:8000 \
  --env-file .env.example \
  fit4110/iot-ingestion:lab04
```

## 4. Check health

```bash
curl http://localhost:8000/health
```

Expected shape:

```json
{
  "status": "ok",
  "service": "iot-ingestion",
  "time": "2026-06-02T03:10:57Z"
}
```

## 5. Run Newman against the container

```bash
npm run test:local
```

Reports are generated at:

```text
reports/newman-lab04-local.xml
reports/newman-lab04-local.html
```

The collection verifies the Lab 03 IoT endpoints:

- `GET /health`
- `POST /events/sensor`
- `POST /telemetry`
- `GET /telemetry/{eventId}`
- `GET /devices/{deviceId}`

Stop the container when done:

```bash
docker stop fit4110-iot-lab04
```
