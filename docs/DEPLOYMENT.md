# Deployment

## Docker Compose
```bash
docker compose up -d --build
```

默认启动的是单个 `app` 服务，容器内同时运行：
- FastAPI（监听容器内 `127.0.0.1:8010`）
- Nginx（对外暴露 `80`，统一转发 `/api` 和静态前端）

## Volumes
- `./photos:/data/photos` (photo root)
- `./cache:/data/cache` (thumbnails)
- `./data:/app/data` (SQLite database)

## Environment
- `PHOTO_ROOT=/data/photos`
- `THUMB_CACHE=/data/cache`
- `THUMB_SIZE=320`
- `DB_PATH=data/app.db`
- `SECRET_KEY` (JWT key)
- `ADMIN_USERNAME` / `ADMIN_PASSWORD`

## Archive Dependencies
- ZIP works out of the box
- 7Z/RAR require full dependencies

Install full dependencies locally:
```bash
cd backend
pip install -r requirements-full.txt
```

If you need 7Z/RAR in Docker, change Dockerfile to install `requirements-full.txt`.

Local setup scripts:
- `scripts/install-archive-deps.ps1`
- `scripts/install-archive-deps.sh`

## Docker Checklist
- Docker Desktop is running
- `docker --version` returns a version
- `docker compose version` returns a version
- `docker compose up -d --build` completes without errors
- Visit `http://localhost:8480` for the UI
- Visit `http://localhost:8480/health` for backend health
