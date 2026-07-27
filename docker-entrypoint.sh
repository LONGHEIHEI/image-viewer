#!/usr/bin/env bash
set -e

# Ensure data/cache directories exist with correct ownership.
# These may be overridden by volume mounts at runtime, so we fix permissions
# at container startup rather than during image build.
for dir in /app/backend/data /app/photos /app/cache; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
    fi
    # If the directory isn't writable, try to fix it via rootless fallback
    if [ ! -w "$dir" ]; then
        echo "WARNING: $dir is not writable by appuser. Check host volume permissions." >&2
    fi
done

exec "$@"
