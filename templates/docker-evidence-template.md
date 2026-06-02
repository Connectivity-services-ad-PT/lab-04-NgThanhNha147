# Docker Evidence Template - Lab 04

## Team

- Team name:
- Service:
- Image tag:

## 1. Build Evidence

Command:

```bash
docker build -t <image-name>:<tag> .
```

Paste build log or screenshot here.

## 2. Run Evidence

Command:

```bash
docker run --rm -p 8000:8000 --env-file .env.example <image-name>:<tag>
```

Paste run log or screenshot here.

## 3. Health Evidence

Command:

```bash
curl http://localhost:8000/health
```

Expected result shape:

```json
{
  "status": "ok",
  "service": "iot-ingestion",
  "time": "2026-06-02T03:12:29Z"
}
```

## 4. Newman Evidence

Command:

```bash
npm run test:local
```

Report paths:

```text
reports/newman-lab04-local.html
reports/newman-lab04-local.xml
```

## 5. Notes

- Known limitation:
- Next step for Lab 05:
