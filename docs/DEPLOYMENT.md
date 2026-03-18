# Deployment

## Docker Compose
```bash
docker compose up -d --build
```

默认启动单个 `app` 服务：
- FastAPI 监听容器内 `0.0.0.0:8010`
- 同时提供后端 API 与前端静态文件

## Volumes
- `${IMAGE_VIEWS_DATA_DIR:-./backend/data}:/app/backend/data` (SQLite database)
- `${IMAGE_VIEWS_PHOTOS_DIR:-./photos}:/app/photos:ro` (photo root, read-only)
- `${IMAGE_VIEWS_CACHE_DIR:-./cache}:/app/cache` (thumbnails)

建议先在项目根目录准备 `photos/` 与 `cache/`，`backend/data/` 会自动创建。

## Port
- 默认映射 `${IMAGE_VIEWS_PORT:-8480}:8010`
- 默认访问地址：`http://localhost:8480`
- 可通过环境变量 `IMAGE_VIEWS_PORT` 覆盖默认端口

## Environment
- `PHOTO_ROOT=/app/photos`
- `THUMB_CACHE=/app/cache`
- `THUMB_SIZE=320`
- `DB_PATH=/app/backend/data/app.db`
- `SECRET_KEY` (JWT key)
- `ADMIN_USERNAME` / `ADMIN_PASSWORD`

## Health Check
- `GET /health`
- `GET /api/health`

## Archive Dependencies
- ZIP works out of the box
- 7Z/RAR require full dependencies

Install full dependencies locally:
```bash
cd backend
pip install -r requirements-full.txt
```

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
- Optional: visit `http://localhost:8480/api/health`
