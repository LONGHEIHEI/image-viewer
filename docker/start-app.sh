#!/bin/sh
set -eu

uvicorn app.main:app --host 127.0.0.1 --port 8010 &
api_pid=$!

cleanup() {
  kill "$api_pid" 2>/dev/null || true
}

trap cleanup INT TERM EXIT

nginx -g 'daemon off;'
