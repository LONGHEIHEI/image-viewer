from pathlib import Path
from app.utils.path import to_relative
from PIL import Image

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
ARCHIVE_EXTS = {'.zip', '.7z', '.rar'}


def get_image_dimensions(path: Path) -> dict[str, int]:
    try:
        with Image.open(path) as image:
            width, height = image.size
    except Exception:
        return {}
    if width <= 0 or height <= 0:
        return {}
    return {
        'width': width,
        'height': height
    }


def _build_image_item(path: Path, root: str) -> dict:
    return {
        'name': path.name,
        'path': to_relative(path, root),
        **get_image_dimensions(path)
    }


def list_folder(folder_path: str, root: str, page: int = 1, page_size: int = 20):
    path = Path(folder_path)
    if not path.exists() or not path.is_dir():
        raise FileNotFoundError(f'Folder not found: {folder_path}')

    folders = []
    image_entries = []
    archives = []

    for entry in sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
        if entry.is_dir():
            folders.append({
                'name': entry.name,
                'path': to_relative(entry, root)
            })
            continue

        ext = entry.suffix.lower()
        if ext in IMAGE_EXTS:
            image_entries.append(entry)
        elif ext in ARCHIVE_EXTS:
            archives.append({
                'name': entry.name,
                'path': to_relative(entry, root)
            })

    total_images = len(image_entries)
    start = (page - 1) * page_size
    end = start + page_size
    images = [_build_image_item(entry, root) for entry in image_entries[start:end]]

    return {
        'folder': to_relative(path, root),
        'folders': folders,
        'images': images,
        'archives': archives,
        'page': page,
        'page_size': page_size,
        'total_images': total_images,
        'has_more': end < total_images
    }


def build_tree(folder_path: str, root: str, depth: int = 2):
    path = Path(folder_path)
    if not path.exists() or not path.is_dir():
        raise FileNotFoundError(f'Folder not found: {folder_path}')

    node = {
        'name': path.name or 'root',
        'path': to_relative(path, root),
        'type': 'folder',
        'children': []
    }

    if depth <= 0:
        return node

    entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    for entry in entries:
        if entry.is_dir():
            node['children'].append(build_tree(entry, root, depth - 1))
            continue

        ext = entry.suffix.lower()
        if ext in ARCHIVE_EXTS:
            node['children'].append({
                'name': entry.name,
                'path': to_relative(entry, root),
                'type': 'archive'
            })

    return node
