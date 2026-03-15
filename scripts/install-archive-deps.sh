#!/usr/bin/env sh
set -e

echo "Installing archive Python dependencies..."
pip install py7zr rarfile

if ! command -v unrar >/dev/null 2>&1 && ! command -v bsdtar >/dev/null 2>&1; then
  echo "RAR support needs an unrar backend. Install unrar or bsdtar."
fi

echo "Done. You can now use .7z and .rar archives."
