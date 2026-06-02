# Docker Lab Guide

## Why Docker Is Needed

Docker packages source code, dependencies, runtime configuration, and the startup command into one image. That makes the service easier to rerun on another machine or in CI.

## Image And Container

```text
Image     = immutable package
Container = running process created from an image
```

Example:

```bash
docker build -t fit4110/iot-ingestion:lab04 .
docker run -p 8000:8000 --env-file .env.example fit4110/iot-ingestion:lab04
```

## Dockerfile Used In This Lab

The submitted Dockerfile is stronger than a minimal example because it includes:

- multi-stage build
- non-root runtime user `appuser`
- runtime configuration through environment variables
- `HEALTHCHECK` calling `/health`
- `.dockerignore` to reduce build context

## Healthcheck

The container must prove that the FastAPI service inside it is ready, not only that the process exists.

```Dockerfile
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()" || exit 1
```

Check it manually:

```bash
docker ps
docker inspect fit4110-iot-lab04
curl http://localhost:8000/health
```

## Secrets

Do not put real secrets in source code or the Dockerfile. This lab uses `AUTH_TOKEN=local-dev-token` only as a local placeholder in `.env.example`.

For a real deployment, pass the token at runtime:

```bash
docker run --env AUTH_TOKEN="<real-token>" ...
```
