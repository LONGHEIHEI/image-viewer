FROM node:20-alpine AS frontend-builder
WORKDIR /build/frontend

COPY frontend/package*.json ./
RUN npm ci --no-audit --no-fund

COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates curl p7zip-full unrar-free \
  && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY backend/ /app/backend/
COPY --from=frontend-builder /build/frontend/dist /app/frontend/dist
# Some backend setups read static files from backend/app/static.
COPY --from=frontend-builder /build/frontend/dist /app/backend/app/static

RUN useradd --create-home --uid 10001 appuser \
  && mkdir -p /app/backend/data /app/photos /app/cache /data /cache \
  && chown -R appuser:appuser /app

RUN chown -R appuser:appuser /data /cache

USER appuser

ENV DB_PATH=/app/backend/data/app.db \
    PHOTO_ROOT=/app/photos \
    PHOTOS_DIR=/app/photos \
    CACHE_DIR=/app/cache

EXPOSE 8010

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8010/api/health || exit 1

WORKDIR /app/backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010"]
