import hashlib
import logging
import os
from io import BytesIO
from pathlib import Path
from PIL import Image
from app.services.archive_reader import stream_archive_image

logger = logging.getLogger(__name__)


def _ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def _thumb_path(cache_root: str, key: str, size: int) -> Path:
    cache_dir = Path(cache_root)
    _ensure_dir(cache_dir)
    return cache_dir / f'{key}_{size}.jpg'


def cleanup_cache(cache_root: str, max_mb: int) -> None:
    cache_dir = Path(cache_root)
    if not cache_dir.exists() or not cache_dir.is_dir():
        return
    files: list[tuple[float, Path]] = []
    total_bytes = 0
    for entry in cache_dir.iterdir():
        if entry.is_file():
            try:
                st = entry.stat()
                files.append((st.st_mtime, entry))
                total_bytes += st.st_size
            except OSError:
                continue
    max_bytes = max_mb * 1024 * 1024
    if total_bytes <= max_bytes:
        return
    logger.info(
        '缩略图缓存 %d MB 超过上限 %d MB，开始清理',
        total_bytes // (1024 * 1024), max_mb
    )
    files.sort(key=lambda x: x[0])
    for _, entry in files:
        try:
            entry.unlink()
            total_bytes -= entry.stat().st_size
        except OSError:
            continue
        if total_bytes <= max_bytes:
            break
    logger.info('缩略图缓存清理完成，当前 %d MB', total_bytes // (1024 * 1024))


def get_thumbnail(image_path: str, cache_root: str, size: int) -> str:
    source = Path(image_path)
    key = hashlib.sha1(str(source).encode('utf-8')).hexdigest()
    thumb_path = _thumb_path(cache_root, key, size)

    if thumb_path.exists():
        return str(thumb_path)

    with Image.open(source) as img:
        img = img.convert('RGB')
        img.thumbnail((size, size))
        img.save(thumb_path, format='JPEG', quality=85)

    return str(thumb_path)


def get_archive_thumbnail(archive_path: str, file_path: str, cache_root: str, size: int) -> str:
    key_raw = f'{archive_path}::{file_path}'
    key = hashlib.sha1(key_raw.encode('utf-8')).hexdigest()
    thumb_path = _thumb_path(cache_root, key, size)

    if thumb_path.exists():
        return str(thumb_path)

    data, _ = stream_archive_image(archive_path, file_path)
    if data is None:
        raise FileNotFoundError('Archive image not found')

    with Image.open(BytesIO(data)) as img:
        img = img.convert('RGB')
        img.thumbnail((size, size))
        img.save(thumb_path, format='JPEG', quality=85)

    return str(thumb_path)
