FROM node:20-alpine AS frontend-builder
WORKDIR /build/frontend

COPY frontend/package*.json ./
RUN npm ci --no-audit --no-fund

COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

ARG INSTALL_ARCHIVE_TOOLS=1
RUN set -eux; \
  apt-get update; \
  apt-get install -y --no-install-recommends ca-certificates gosu; \
  if [ "$INSTALL_ARCHIVE_TOOLS" = "1" ]; then \
    apt-get install -y --no-install-recommends p7zip-full unrar-free; \
  fi; \
  rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --no-compile -r /tmp/requirements.txt

COPY backend/app/ /app/backend/app/
COPY --from=frontend-builder /build/frontend/dist /app/frontend/dist
COPY --from=frontend-builder /build/frontend/dist /app/backend/app/static
RUN find /app/backend/app/static -type f -name "*.map" -delete

RUN useradd --create-home --uid 10001 appuser

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENV DB_PATH=/app/backend/data/app.db \
    PHOTO_ROOT=/app/photos \
    THUMB_CACHE=/app/cache

EXPOSE 8010

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8010/api/health', timeout=3)" || exit 1

WORKDIR /app/backend
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--port", "8010"]
