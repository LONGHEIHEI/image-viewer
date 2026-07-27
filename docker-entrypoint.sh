#!/usr/bin/env bash
set -e

# Fix directory ownership for volume mounts. Docker creates bind-mount
# directories as root; chown them so appuser can read/write.
for dir in /app/backend/data /app/photos /app/cache; do
    mkdir -p "$dir"
    owner=$(stat -c '%u' "$dir" 2>/dev/null || echo "0")
    if [ "$owner" != "10001" ]; then
        chown 10001:10001 "$dir" 2>/dev/null || true
    fi
done

exec gosu appuser "$@"
