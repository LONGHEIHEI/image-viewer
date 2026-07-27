import hashlib
from io import BytesIO
from pathlib import Path
from PIL import Image
from app.services.archive_reader import stream_archive_image


def _ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def _thumb_path(cache_root: str, key: str, size: int) -> Path:
    cache_dir = Path(cache_root)
    _ensure_dir(cache_dir)
    return cache_dir / f'{key}_{size}.jpg'


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
