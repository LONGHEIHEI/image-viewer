FROM node:20-alpine AS frontend-build

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend /frontend
RUN npm run build

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx p7zip-full unrar-free \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /etc/nginx/conf.d/default.conf

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app /app/app
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY docker/start-app.sh /usr/local/bin/start-app.sh
COPY --from=frontend-build /frontend/dist /usr/share/nginx/html

RUN chmod +x /usr/local/bin/start-app.sh

ENV PYTHONUNBUFFERED=1
ENV PHOTO_ROOT=/data/photos
ENV THUMB_CACHE=/data/cache
ENV THUMB_SIZE=320

EXPOSE 80

CMD ["start-app.sh"]
