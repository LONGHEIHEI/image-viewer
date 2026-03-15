from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import FileResponse, Response
import random
from pathlib import Path
from app.config import Settings
from app.services.fs_indexer import list_folder, build_tree, IMAGE_EXTS
from app.services.archive_reader import list_archive, stream_archive_image, ArchiveSupportError
from app.services.thumbnailer import get_thumbnail, get_archive_thumbnail
from app.services.deps import get_current_user
from app.utils.path import resolve_under_root, rel_from_abs, is_within_allowed, is_within_or_ancestor, normalize_rel

router = APIRouter()
settings = Settings()


def safe_resolve(subpath: str) -> str:
    try:
        return resolve_under_root(settings.photo_root, subpath)
    except ValueError:
        raise HTTPException(status_code=400, detail='路径非法')


def safe_list_folder(path: str, page: int, page_size: int):
    try:
        return list_folder(path, settings.photo_root, page=page, page_size=page_size)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='目录不存在，请检查路径')


def safe_list_archive(path: str, page: int, page_size: int):
    try:
        return list_archive(path, settings.photo_root, page=page, page_size=page_size)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='压缩包不存在，请检查路径')
    except ArchiveSupportError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


def require_allowed_paths(user: dict) -> list[str]:
    if user.get('is_admin'):
        return ['']
    allowed = user.get('allowed_paths', [])
    if not allowed:
        raise HTTPException(status_code=403, detail='未配置可访问目录')
    return allowed


def filter_listing(listing: dict, allowed_paths: list[str]):
    if not allowed_paths or '' in [normalize_rel(p) for p in allowed_paths]:
        return listing

    listing['folders'] = [
        f for f in listing['folders']
        if is_within_or_ancestor(normalize_rel(f['path']), allowed_paths)
    ]
    listing['archives'] = [
        a for a in listing['archives']
        if is_within_allowed(normalize_rel(a['path']), allowed_paths)
    ]
    listing['images'] = [
        i for i in listing['images']
        if is_within_allowed(normalize_rel(i['path']), allowed_paths)
    ]
    return listing


def build_tree_for_user(root_abs: str, allowed_paths: list[str], depth: int):
    if not allowed_paths or '' in [normalize_rel(p) for p in allowed_paths]:
        return build_tree(root_abs, settings.photo_root, depth=depth)

    root_node = {
        'name': 'root',
        'path': '',
        'type': 'folder',
        'children': []
    }

    for allowed in allowed_paths:
        allowed_norm = normalize_rel(allowed)
        if allowed_norm == '':
            return build_tree(root_abs, settings.photo_root, depth=depth)
        try:
            abs_path = resolve_under_root(settings.photo_root, allowed_norm)
            node = build_tree(abs_path, settings.photo_root, depth=depth)
            root_node['children'].append(node)
        except FileNotFoundError:
            continue

    return root_node


def _random_image_in_folder(abs_path: str) -> str | None:
    folder = Path(abs_path)
    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(abs_path)
    candidates = [
        entry for entry in folder.iterdir()
        if entry.is_file() and entry.suffix.lower() in IMAGE_EXTS
    ]
    if not candidates:
        return None
    return str(random.choice(candidates))


@router.get('/tree')
def get_tree(
    root: str = Query(default=''),
    depth: int = Query(default=2, ge=0, le=6),
    user: dict = Depends(get_current_user)
):
    base = safe_resolve(root)
    allowed = require_allowed_paths(user)
    return build_tree_for_user(base, allowed, depth)


@router.get('/folder')
def get_folder(
    path: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=500),
    user: dict = Depends(get_current_user)
):
    allowed = require_allowed_paths(user)
    base = safe_resolve(path)
    rel_path = rel_from_abs(base, settings.photo_root)
    if not is_within_or_ancestor(rel_path, allowed):
        raise HTTPException(status_code=403, detail='无权限访问')
    listing = safe_list_folder(base, page, page_size)
    return filter_listing(listing, allowed)


@router.get('/folder/cover')
def get_folder_cover(path: str, user: dict = Depends(get_current_user)):
    allowed = require_allowed_paths(user)
    base = safe_resolve(path)
    rel_path = rel_from_abs(base, settings.photo_root)
    if not is_within_or_ancestor(rel_path, allowed):
        raise HTTPException(status_code=403, detail='无权限访问')
    try:
        image_path = _random_image_in_folder(base)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='目录不存在，请检查路径')
    if not image_path:
        raise HTTPException(status_code=404, detail='目录内没有图片')
    thumb_path = get_thumbnail(image_path, settings.thumb_cache, settings.thumb_size)
    return FileResponse(thumb_path)


@router.get('/archive')
def get_archive(
    path: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=500),
    user: dict = Depends(get_current_user)
):
    allowed = require_allowed_paths(user)
    archive_path = safe_resolve(path)
    rel_path = rel_from_abs(archive_path, settings.photo_root)
    if not is_within_allowed(rel_path, allowed):
        raise HTTPException(status_code=403, detail='无权限访问')
    return safe_list_archive(archive_path, page, page_size)


@router.get('/image')
def get_image(path: str, user: dict = Depends(get_current_user)):
    allowed = require_allowed_paths(user)
    file_path = safe_resolve(path)
    rel_path = rel_from_abs(file_path, settings.photo_root)
    if not is_within_allowed(rel_path, allowed):
        raise HTTPException(status_code=403, detail='无权限访问')
    return FileResponse(file_path)


@router.get('/archive/image')
def get_archive_image(path: str, file: str, user: dict = Depends(get_current_user)):
    allowed = require_allowed_paths(user)
    archive_path = safe_resolve(path)
    rel_path = rel_from_abs(archive_path, settings.photo_root)
    if not is_within_allowed(rel_path, allowed):
        raise HTTPException(status_code=403, detail='无权限访问')
    try:
        content, media_type = stream_archive_image(archive_path, file)
    except ArchiveSupportError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if content is None:
        raise HTTPException(status_code=404, detail='压缩包内未找到图片')
    return Response(content=content, media_type=media_type)


@router.get('/thumb')
def get_thumb(path: str, user: dict = Depends(get_current_user)):
    allowed = require_allowed_paths(user)
    file_path = safe_resolve(path)
    rel_path = rel_from_abs(file_path, settings.photo_root)
    if not is_within_allowed(rel_path, allowed):
        raise HTTPException(status_code=403, detail='无权限访问')
    thumb_path = get_thumbnail(file_path, settings.thumb_cache, settings.thumb_size)
    return FileResponse(thumb_path)


@router.get('/archive/thumb')
def get_archive_thumb(path: str, file: str, user: dict = Depends(get_current_user)):
    allowed = require_allowed_paths(user)
    archive_path = safe_resolve(path)
    rel_path = rel_from_abs(archive_path, settings.photo_root)
    if not is_within_allowed(rel_path, allowed):
        raise HTTPException(status_code=403, detail='无权限访问')
    try:
        thumb_path = get_archive_thumbnail(archive_path, file, settings.thumb_cache, settings.thumb_size)
    except ArchiveSupportError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='压缩包内未找到图片')
    return FileResponse(thumb_path)
