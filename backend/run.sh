#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
PROJECT_ROOT="$(cd .. && pwd)"

if [ ! -d .venv ]; then
    python3 -m venv .venv
    . .venv/bin/activate
    pip install -r requirements.txt
else
    . .venv/bin/activate
fi

export PHOTO_ROOT="${PROJECT_ROOT}/photos"
export THUMB_CACHE="${PROJECT_ROOT}/cache"
export DB_PATH="${PROJECT_ROOT}/data/app.db"

mkdir -p "${PROJECT_ROOT}/photos" "${PROJECT_ROOT}/cache" "${PROJECT_ROOT}/data"

uvicorn app.main:app --reload --host localhost --port 8010
