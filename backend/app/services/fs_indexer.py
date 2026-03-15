from pathlib import Path
from app.utils.path import to_relative

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
ARCHIVE_EXTS = {'.zip', '.7z', '.rar'}


def list_folder(folder_path: str, root: str, page: int = 1, page_size: int = 20):
    path = Path(folder_path)
    if not path.exists() or not path.is_dir():
        raise FileNotFoundError(f'Folder not found: {folder_path}')

    folders = []
    images_all = []
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
            images_all.append({
                'name': entry.name,
                'path': to_relative(entry, root)
            })
        elif ext in ARCHIVE_EXTS:
            archives.append({
                'name': entry.name,
                'path': to_relative(entry, root)
            })

    total_images = len(images_all)
    start = (page - 1) * page_size
    end = start + page_size
    images = images_all[start:end]

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
