# Troubleshooting

| Problem | Likely Cause | Fix |
|---|---|---|
| `Cannot connect to Docker daemon` | Docker Desktop or Docker Engine is not running | Start Docker Desktop and wait until `docker info` works |
| `port is already allocated` | Another process uses port `8000` | Stop that process or run with `-p 8001:8000` and update Postman `baseUrl` |
| `ModuleNotFoundError` | Wrong app module or missing dependency | Check `requirements.txt` and Docker `CMD` |
| `/health` does not respond | Container is not ready or wrong port mapping | Run `docker logs fit4110-iot-lab04` |
| Newman `ECONNREFUSED` | Container is not running or Postman environment has the wrong `baseUrl` | Start the container and verify `http://localhost:8000/health` |
| Auth tests fail | `AUTH_TOKEN` differs between `.env.example` and Postman environment | Keep both as `local-dev-token` for local lab runs |
| Image is too large | Build context includes `.git`, `.venv`, or `node_modules` | Check `.dockerignore` |
| Container runs as root | Dockerfile is missing `USER appuser` | Add a non-root user and switch to it |
| CI fails before Newman | Service was not ready | Wait for `/health` with `wait-on` or `scripts/wait-for-health.sh` |
