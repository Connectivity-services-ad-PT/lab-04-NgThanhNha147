# Docker Evidence - Lab 04

## Team

- Team name: `team-iot`
- Service: `iot-ingestion`
- Image tags:
  - `fit4110/iot-ingestion:lab04`
  - `fit4110/iot-ingestion:v0.1.0-team-iot`

## Build Evidence

Command:

```bash
docker build -t fit4110/iot-ingestion:lab04 .
```

Result: build completed successfully.

Image inspect summary:

```text
User: appuser
Healthcheck: GET http://127.0.0.1:8000/health
```

## Run Evidence

Command:

```bash
docker run -d --rm --name fit4110-iot-lab04 -p 8000:8000 --env-file .env.example fit4110/iot-ingestion:lab04
```

Result:

```text
Container status: running
Container health: healthy
Container user: appuser
```

## Health Evidence

Command:

```bash
curl http://localhost:8000/health
```

Observed response:

```json
{"status":"ok","service":"iot-ingestion","time":"2026-06-02T03:31:47Z"}
```

## Newman Evidence

Command:

```bash
npm run test:local
```

Result:

```text
Requests: 13 executed, 0 failed
Assertions: 23 executed, 0 failed
Average response time: 8 ms
```

Mock verification was also checked with `npm run test:mock`: 13 requests, 23 assertions, 0 failed.

Report files:

```text
reports/newman-lab04-local.xml
reports/newman-lab04-local.html
```
