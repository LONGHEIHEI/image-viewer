from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.responses import FileResponse, Response
import random
from pathlib import Path
from pydantic import BaseModel
from typing import List
from app.services import db
from app.services.auth import hash_password, verify_password, create_collection_token, decode_token
from app.services.deps import get_current_user, require_admin
from app.services.fs_indexer import list_folder, IMAGE_EXTS, ARCHIVE_EXTS, build_tree
from app.services.archive_reader import (
    list_archive,
    stream_archive_image,
    get_archive_cover_file,
    ArchiveSupportError
)
from app.services.thumbnailer import get_thumbnail, get_archive_thumbnail
from app.config import Settings
from app.utils.path import (
    resolve_any_path,
    rel_from_abs,
    is_within_allowed,
    is_within_or_ancestor,
    normalize_path,
    to_relative
)

router = APIRouter()
settings = Settings()


class CollectionCreate(BaseModel):
    name: str
    paths: List[str]
    password: str | None = None
    cover_path: str | None = None
    aggregate_subdirs: bool = False


class CollectionUpdate(BaseModel):
    name: str | None = None
    paths: List[str] | None = None
    password: str | None = None
    clear_password: bool = False
    cover_path: str | None = None
    clear_cover: bool = False
    aggregate_subdirs: bool | None = None


class CollectionAccess(BaseModel):
    password: str | None = None


def _normalize_paths(paths: List[str]) -> List[str]:
    cleaned: List[str] = []
    for path in paths:
        norm = normalize_path(path)
        if not norm:
            continue
        if norm not in cleaned:
            cleaned.append(norm)
    return cleaned


def _normalize_path_for_listing(path: str) -> str:
    abs_path = resolve_any_path(settings.photo_root, path)
    rel = rel_from_abs(abs_path, settings.photo_root)
    return normalize_path(rel)


def _normalize_paths_for_listing(paths: List[str]) -> List[str]:
    cleaned: List[str] = []
    for path in paths:
        norm = _normalize_path_for_listing(path)
        if norm not in cleaned:
            cleaned.append(norm)
    return cleaned


def _collection_accessible(collection_paths: List[str], user_allowed: List[str]) -> bool:
    collection_norm = _normalize_paths_for_listing(collection_paths)
    allowed_norm = _normalize_paths_for_listing(user_allowed)
    if not user_allowed or '' in allowed_norm:
        return True
    for path in collection_norm:
        if is_within_allowed(path, allowed_norm) or is_within_or_ancestor(path, allowed_norm):
            return True
    return False


def _get_collection_or_404(collection_id: int) -> dict:
    collection = db.get_collection_by_id(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail='集合不存在')
    return collection


def _require_collection_token(collection: dict, request: Request, user: dict):
    if user.get('is_admin'):
        return
    if not collection.get('password_hash'):
        return
    token = request.headers.get('X-Collection-Token') or request.query_params.get('ct')
    if not token:
        raise HTTPException(status_code=401, detail='集合需要密码')
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail='集合访问凭证无效')
    if payload.get('typ') != 'collection' or payload.get('cid') != collection['id']:
        raise HTTPException(status_code=401, detail='集合访问凭证无效')


def _filter_listing(listing: dict, allowed_paths: List[str]):
    if not allowed_paths:
        return listing
    normalized: List[str] = []
    allow_all = False
    for p in allowed_paths:
        norm = _normalize_path_for_listing(p)
        if norm == '':
            allow_all = True
            break
        if norm not in normalized:
            normalized.append(norm)
    if allow_all:
        return listing

    listing['folders'] = [
        f for f in listing['folders']
        if is_within_or_ancestor(_normalize_path_for_listing(f['path']), normalized)
    ]
    listing['archives'] = [
        a for a in listing['archives']
        if is_within_allowed(_normalize_path_for_listing(a['path']), normalized)
    ]
    listing['images'] = [
        i for i in listing['images']
        if is_within_allowed(_normalize_path_for_listing(i['path']), normalized)
    ]
    return listing


def _normalize_listing_paths(listing: dict) -> dict:
    if 'folder' in listing and listing['folder'] is not None:
        listing['folder'] = normalize_path(listing['folder'])
    if 'archive' in listing and listing['archive'] is not None:
        listing['archive'] = normalize_path(listing['archive'])
    for key in ['folders', 'archives', 'images', 'files']:
        if key not in listing:
            continue
        listing[key] = [
            {**item, 'path': normalize_path(item['path'])}
            for item in listing[key]
        ]
    return listing


def _collection_root_listing(collection_paths: List[str]):
    names = [p.split('/')[-1] if '/' in p else p for p in collection_paths]
    name_count = {n: names.count(n) for n in set(names)}
    folders = []
    for path in collection_paths:
        base = path.split('/')[-1] if '/' in path else path
        display = path if name_count.get(base, 0) > 1 else base
        folders.append({'name': display, 'path': path})
    return {
        'folder': '',
        'folders': folders,
        'images': [],
        'archives': [],
        'page': 1,
        'page_size': 20,
        'total_images': 0,
        'has_more': False
    }


def _build_collection_tree(collection_paths: List[str], allowed_paths: List[str], depth: int):
    root_node = {
        'name': 'root',
        'path': '',
        'type': 'folder',
        'children': []
    }
    for path in collection_paths:
        if not (is_within_allowed(path, allowed_paths) or is_within_or_ancestor(path, allowed_paths)):
            continue
        abs_path = resolve_any_path(settings.photo_root, path)
        target = Path(abs_path)
        if target.exists() and target.is_file():
            if target.suffix.lower() in ARCHIVE_EXTS:
                root_node['children'].append({
                    'name': target.name,
                    'path': normalize_path(path),
                    'type': 'archive'
                })
            continue
        try:
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


def _find_first_image_in_tree(folder: Path, max_depth: int = 2) -> str | None:
    if max_depth < 0:
        return None
    try:
        entries = sorted(folder.iterdir(), key=lambda p: p.name.lower())
    except PermissionError:
        return None
    for entry in entries:
        if entry.is_file() and entry.suffix.lower() in IMAGE_EXTS:
            return str(entry)
    if max_depth == 0:
        return None
    for entry in entries:
        if entry.is_dir():
            found = _find_first_image_in_tree(entry, max_depth - 1)
            if found:
                return found
    return None


def _collect_images_in_tree(folder: Path, root: str, max_depth: int) -> list[dict]:
    images: list[dict] = []
    if max_depth < 0:
        return images
    try:
        entries = sorted(folder.iterdir(), key=lambda p: p.name.lower())
    except PermissionError:
        return images
    for entry in entries:
        if entry.is_file() and entry.suffix.lower() in IMAGE_EXTS:
            images.append({'name': entry.name, 'path': to_relative(entry, root)})
        elif entry.is_dir() and max_depth > 0:
            images.extend(_collect_images_in_tree(entry, root, max_depth - 1))
    return images


def _store_cover_path(abs_path: str, collection_paths: List[str]) -> str:
    return _normalize_path_for_listing(abs_path)


def _find_first_image_in_dir(dir_path: Path) -> str | None:
    try:
        entries = sorted(dir_path.iterdir(), key=lambda p: p.name.lower())
    except PermissionError:
        return None
    for entry in entries:
        if entry.is_file() and entry.suffix.lower() in IMAGE_EXTS:
            return str(entry)
    return None


def _select_collection_cover(collection_paths: List[str]) -> str | None:
    for path in collection_paths:
        abs_path = resolve_any_path(settings.photo_root, path)
        target = Path(abs_path)
        if target.is_file() and target.suffix.lower() in IMAGE_EXTS:
            return str(target)
        if target.is_dir():
            found = _find_first_image_in_dir(target)
            if not found:
                found = _find_first_image_in_tree(target, max_depth=2)
            if found:
                return found
    return None


def _normalize_cover_path(cover_path: str, collection_paths: List[str]) -> str:
    norm = _normalize_path_for_listing(cover_path)
    if not norm:
        raise HTTPException(status_code=400, detail='封面路径不能为空')
    collection_norm = _normalize_paths_for_listing(collection_paths)
    if not is_within_allowed(norm, collection_norm):
        raise HTTPException(status_code=400, detail='封面路径不在集合内')
    abs_path = resolve_any_path(settings.photo_root, cover_path)
    target = Path(abs_path)
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=400, detail='封面图不存在')
    if target.suffix.lower() not in IMAGE_EXTS:
        raise HTTPException(status_code=400, detail='封面必须是图片')
    return norm


@router.get('/collections/available')
def list_collections_available(user: dict = Depends(get_current_user)):
    collections = db.list_collections()
    allowed = user.get('allowed_paths', [])
    if user.get('is_admin'):
        return [
            {
                'id': c['id'],
                'name': c['name'],
                'requires_password': bool(c.get('password_hash')),
                'cover_path': c.get('cover_path')
            }
            for c in collections
        ]
    return [
        {
            'id': c['id'],
            'name': c['name'],
            'requires_password': bool(c.get('password_hash')),
            'cover_path': c.get('cover_path')
        }
        for c in collections
        if _collection_accessible(c['paths'], allowed)
    ]


@router.get('/collections', dependencies=[Depends(require_admin)])
def list_collections_admin():
    collections = db.list_collections()
    return [
        {
            'id': c['id'],
            'name': c['name'],
            'paths': c['paths'],
            'requires_password': bool(c.get('password_hash')),
            'cover_path': c.get('cover_path'),
            'aggregate_subdirs': bool(c.get('aggregate_subdirs')),
            'created_at': c['created_at']
        }
        for c in collections
    ]


@router.get('/collections/{collection_id}')
def get_collection(collection_id: int, user: dict = Depends(get_current_user)):
    collection = _get_collection_or_404(collection_id)
    return {
        'id': collection['id'],
        'name': collection['name'],
        'requires_password': bool(collection.get('password_hash')),
        'cover_path': collection.get('cover_path'),
        'aggregate_subdirs': bool(collection.get('aggregate_subdirs'))
    }


@router.post('/collections', dependencies=[Depends(require_admin)])
def create_collection(payload: CollectionCreate):
    if db.get_collection_by_name(payload.name):
        raise HTTPException(status_code=400, detail='集合名称已存在')
    paths = _normalize_paths(payload.paths)
    if not paths:
        raise HTTPException(status_code=400, detail='集合路径不能为空')
    password_hash = hash_password(payload.password) if payload.password else None
    cover_path = None
    if payload.cover_path:
        cover_path = _normalize_cover_path(payload.cover_path, paths)
    db.create_collection(
        payload.name,
        paths,
        password_hash,
        cover_path,
        payload.aggregate_subdirs
    )
    return {'status': 'ok'}


@router.put('/collections/{collection_id}', dependencies=[Depends(require_admin)])
def update_collection(collection_id: int, payload: CollectionUpdate):
    collection = db.get_collection_by_id(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail='集合不存在')
    paths = _normalize_paths(payload.paths) if payload.paths is not None else collection['paths']
    password_hash = hash_password(payload.password) if payload.password else None
    cover_path = None
    if payload.cover_path is not None and payload.cover_path != '':
        cover_path = _normalize_cover_path(payload.cover_path, paths)
    db.update_collection(
        collection_id,
        name=payload.name,
        paths=_normalize_paths(payload.paths) if payload.paths is not None else None,
        password_hash=password_hash,
        clear_password=payload.clear_password,
        cover_path=cover_path,
        clear_cover=payload.clear_cover,
        aggregate_subdirs=payload.aggregate_subdirs
    )
    return {'status': 'ok'}


@router.delete('/collections/{collection_id}')
def delete_collection(collection_id: int):
    if not db.get_collection_by_id(collection_id):
        raise HTTPException(status_code=404, detail='集合不存在')
    db.delete_collection(collection_id)
    return {'status': 'ok'}


@router.post('/collections/{collection_id}/access')
def access_collection(collection_id: int, payload: CollectionAccess, user: dict = Depends(get_current_user)):
    collection = _get_collection_or_404(collection_id)
    allowed = user.get('allowed_paths', [])
    if not user.get('is_admin') and not _collection_accessible(collection['paths'], allowed):
        raise HTTPException(status_code=403, detail='无权限访问该集合')
    if collection.get('password_hash'):
        if not payload.password or not verify_password(payload.password, collection['password_hash']):
            raise HTTPException(status_code=401, detail='集合密码错误')
        return {'token': create_collection_token(collection_id)}
    return {'token': ''}


@router.get('/collections/{collection_id}/cover')
def collection_cover(collection_id: int, request: Request, user: dict = Depends(get_current_user)):
    collection = _get_collection_or_404(collection_id)
    _require_collection_token(collection, request, user)
    allowed = user.get('allowed_paths', [])
    if user.get('is_admin'):
        allowed = ['']
    if not allowed:
        raise HTTPException(status_code=403, detail='未配置可访问目录')

    collection_paths = _normalize_paths_for_listing(collection['paths'])
    allowed_norm = _normalize_paths_for_listing(allowed)
    eligible_paths = collection_paths
    if allowed and '' not in allowed_norm:
        eligible_paths = [
            p for p in collection_paths
            if is_within_allowed(p, allowed_norm) or is_within_or_ancestor(p, allowed_norm)
        ]

    cover_path = collection.get('cover_path')
    abs_path = None
    if cover_path:
        norm = _normalize_path_for_listing(cover_path)
        if is_within_allowed(norm, eligible_paths):
            candidate = resolve_any_path(settings.photo_root, cover_path)
            target = Path(candidate)
            if target.exists() and target.is_file() and target.suffix.lower() in IMAGE_EXTS:
                abs_path = candidate

    if abs_path is None:
        abs_path = _select_collection_cover(eligible_paths)
        if abs_path:
            store_path = _store_cover_path(abs_path, collection_paths)
            db.update_collection(collection_id, cover_path=store_path)

    if abs_path is None:
        raise HTTPException(status_code=404, detail='未找到可用封面')

    thumb_path = get_thumbnail(abs_path, settings.thumb_cache, settings.thumb_size)
    return FileResponse(thumb_path)


@router.get('/collections/{collection_id}/tree')
def collection_tree(
    collection_id: int,
    request: Request,
    depth: int = Query(default=2, ge=0, le=6),
    user: dict = Depends(get_current_user)
):
    collection = _get_collection_or_404(collection_id)
    _require_collection_token(collection, request, user)
    allowed = user.get('allowed_paths', [])
    if user.get('is_admin'):
        allowed = ['']
    if not allowed:
        raise HTTPException(status_code=403, detail='未配置可访问目录')

    collection_paths = _normalize_paths_for_listing(collection['paths'])
    return _build_collection_tree(collection_paths, allowed, depth)


@router.get('/collections/{collection_id}/folder')
def collection_folder(
    collection_id: int,
    request: Request,
    path: str = Query(default=''),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=500),
    view: str = Query(default='folder'),
    flat_depth: int = Query(default=3, ge=0, le=8),
    user: dict = Depends(get_current_user)
):
    collection = _get_collection_or_404(collection_id)
    _require_collection_token(collection, request, user)
    allowed = user.get('allowed_paths', [])
    if user.get('is_admin'):
        allowed = ['']
    if not allowed:
        raise HTTPException(status_code=403, detail='未配置可访问目录')

    collection_paths = _normalize_paths_for_listing(collection['paths'])
    allowed_norm = _normalize_paths_for_listing(allowed)
    if path == '':
        if '' in collection_paths:
            abs_path = resolve_any_path(settings.photo_root, '')
            try:
                listing = list_folder(abs_path, settings.photo_root, page=page, page_size=page_size)
            except FileNotFoundError:
                raise HTTPException(status_code=404, detail='目录不存在，请检查路径')
            if view == 'flat':
                images_all = _collect_images_in_tree(Path(abs_path), settings.photo_root, flat_depth)
                total_images = len(images_all)
                start = (page - 1) * page_size
                end = start + page_size
                listing['images'] = images_all[start:end]
                listing['total_images'] = total_images
                listing['has_more'] = end < total_images
            listing = _normalize_listing_paths(listing)
            listing = _filter_listing(listing, collection_paths)
            listing = _filter_listing(listing, allowed_norm)
            return listing
        listing = _collection_root_listing(collection_paths)
        listing = _filter_listing(listing, allowed)
        return listing

    rel_path = _normalize_path_for_listing(path)
    if not is_within_or_ancestor(rel_path, collection_paths):
        raise HTTPException(status_code=403, detail='不在集合路径内')
    if '' not in allowed_norm and not is_within_or_ancestor(rel_path, allowed_norm):
        raise HTTPException(status_code=403, detail='无权限访问')

    abs_path = resolve_any_path(settings.photo_root, rel_path)
    try:
        listing = list_folder(abs_path, settings.photo_root, page=page, page_size=page_size)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='目录不存在，请检查路径')
    if view == 'flat':
        images_all = _collect_images_in_tree(Path(abs_path), settings.photo_root, flat_depth)
        total_images = len(images_all)
        start = (page - 1) * page_size
        end = start + page_size
        listing['images'] = images_all[start:end]
        listing['total_images'] = total_images
        listing['has_more'] = end < total_images
    listing = _normalize_listing_paths(listing)
    listing = _filter_listing(listing, collection_paths)
    listing = _filter_listing(listing, allowed_norm)
    return listing


@router.get('/collections/{collection_id}/folder/cover')
def collection_folder_cover(
    collection_id: int,
    request: Request,
    path: str,
    user: dict = Depends(get_current_user)
):
    collection = _get_collection_or_404(collection_id)
    _require_collection_token(collection, request, user)
    allowed = user.get('allowed_paths', [])
    if user.get('is_admin'):
        allowed = ['']
    if not allowed:
        raise HTTPException(status_code=403, detail='未配置可访问目录')

    rel_path = _normalize_path_for_listing(path)
    collection_paths = _normalize_paths_for_listing(collection['paths'])
    allowed_norm = _normalize_paths_for_listing(allowed)
    if not is_within_or_ancestor(rel_path, collection_paths):
        raise HTTPException(status_code=403, detail='不在集合路径内')
    if '' not in allowed_norm and not is_within_or_ancestor(rel_path, allowed_norm):
        raise HTTPException(status_code=403, detail='无权限访问')

    abs_path = resolve_any_path(settings.photo_root, rel_path)
    try:
        image_path = _random_image_in_folder(abs_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='目录不存在，请检查路径')
    if not image_path:
        image_path = _find_first_image_in_tree(Path(abs_path), max_depth=2)
    if not image_path:
        raise HTTPException(status_code=404, detail='目录内没有图片')
    thumb_path = get_thumbnail(image_path, settings.thumb_cache, settings.thumb_size)
    return FileResponse(thumb_path)


@router.get('/collections/{collection_id}/archive')
def collection_archive(
    collection_id: int,
    request: Request,
    path: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=500),
    user: dict = Depends(get_current_user)
):
    collection = _get_collection_or_404(collection_id)
    _require_collection_token(collection, request, user)
    allowed = user.get('allowed_paths', [])
    if user.get('is_admin'):
        allowed = ['']
    if not allowed:
        raise HTTPException(status_code=403, detail='未配置可访问目录')

    rel_path = _normalize_path_for_listing(path)
    collection_paths = _normalize_paths_for_listing(collection['paths'])
    allowed_norm = _normalize_paths_for_listing(allowed)
    if not is_within_allowed(rel_path, collection_paths):
        raise HTTPException(status_code=403, detail='不在集合路径内')
    if '' not in allowed_norm and not is_within_allowed(rel_path, allowed_norm):
        raise HTTPException(status_code=403, detail='无权限访问')

    abs_path = resolve_any_path(settings.photo_root, rel_path)
    try:
        listing = list_archive(abs_path, settings.photo_root, page=page, page_size=page_size)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='压缩包不存在，请检查路径')
    except ArchiveSupportError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _normalize_listing_paths(listing)


@router.get('/collections/{collection_id}/image')
def collection_image(collection_id: int, path: str, request: Request, user: dict = Depends(get_current_user)):
    collection = _get_collection_or_404(collection_id)
    _require_collection_token(collection, request, user)
    allowed = user.get('allowed_paths', [])
    if user.get('is_admin'):
        allowed = ['']
    if not allowed:
        raise HTTPException(status_code=403, detail='未配置可访问目录')

    rel_path = _normalize_path_for_listing(path)
    collection_paths = _normalize_paths_for_listing(collection['paths'])
    allowed_norm = _normalize_paths_for_listing(allowed)
    if not is_within_allowed(rel_path, collection_paths):
        raise HTTPException(status_code=403, detail='不在集合路径内')
    if '' not in allowed_norm and not is_within_allowed(rel_path, allowed_norm):
        raise HTTPException(status_code=403, detail='无权限访问')

    abs_path = resolve_any_path(settings.photo_root, rel_path)
    return FileResponse(abs_path)


@router.get('/collections/{collection_id}/thumb')
def collection_thumb(collection_id: int, path: str, request: Request, user: dict = Depends(get_current_user)):
    collection = _get_collection_or_404(collection_id)
    _require_collection_token(collection, request, user)
    allowed = user.get('allowed_paths', [])
    if user.get('is_admin'):
        allowed = ['']
    if not allowed:
        raise HTTPException(status_code=403, detail='未配置可访问目录')

    rel_path = _normalize_path_for_listing(path)
    collection_paths = _normalize_paths_for_listing(collection['paths'])
    allowed_norm = _normalize_paths_for_listing(allowed)
    if not is_within_allowed(rel_path, collection_paths):
        raise HTTPException(status_code=403, detail='不在集合路径内')
    if '' not in allowed_norm and not is_within_allowed(rel_path, allowed_norm):
        raise HTTPException(status_code=403, detail='无权限访问')

    abs_path = resolve_any_path(settings.photo_root, rel_path)
    thumb_path = get_thumbnail(abs_path, settings.thumb_cache, settings.thumb_size)
    return FileResponse(thumb_path)


@router.get('/collections/{collection_id}/archive/image')
def collection_archive_image(
    collection_id: int,
    request: Request,
    path: str,
    file: str,
    user: dict = Depends(get_current_user)
):
    collection = _get_collection_or_404(collection_id)
    _require_collection_token(collection, request, user)
    allowed = user.get('allowed_paths', [])
    if user.get('is_admin'):
        allowed = ['']
    if not allowed:
        raise HTTPException(status_code=403, detail='未配置可访问目录')

    rel_path = _normalize_path_for_listing(path)
    collection_paths = _normalize_paths_for_listing(collection['paths'])
    allowed_norm = _normalize_paths_for_listing(allowed)
    if not is_within_allowed(rel_path, collection_paths):
        raise HTTPException(status_code=403, detail='不在集合路径内')
    if '' not in allowed_norm and not is_within_allowed(rel_path, allowed_norm):
        raise HTTPException(status_code=403, detail='无权限访问')

    abs_path = resolve_any_path(settings.photo_root, rel_path)
    try:
        content, media_type = stream_archive_image(abs_path, file)
    except ArchiveSupportError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if content is None:
        raise HTTPException(status_code=404, detail='压缩包内未找到图片')
    return Response(content=content, media_type=media_type)


@router.get('/collections/{collection_id}/archive/thumb')
def collection_archive_thumb(
    collection_id: int,
    request: Request,
    path: str,
    file: str,
    user: dict = Depends(get_current_user)
):
    collection = _get_collection_or_404(collection_id)
    _require_collection_token(collection, request, user)
    allowed = user.get('allowed_paths', [])
    if user.get('is_admin'):
        allowed = ['']
    if not allowed:
        raise HTTPException(status_code=403, detail='未配置可访问目录')

    rel_path = _normalize_path_for_listing(path)
    collection_paths = _normalize_paths_for_listing(collection['paths'])
    allowed_norm = _normalize_paths_for_listing(allowed)
    if not is_within_allowed(rel_path, collection_paths):
        raise HTTPException(status_code=403, detail='不在集合路径内')
    if '' not in allowed_norm and not is_within_allowed(rel_path, allowed_norm):
        raise HTTPException(status_code=403, detail='无权限访问')

    abs_path = resolve_any_path(settings.photo_root, rel_path)
    try:
        thumb_path = get_archive_thumbnail(abs_path, file, settings.thumb_cache, settings.thumb_size)
    except ArchiveSupportError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='压缩包内未找到图片')
    return FileResponse(thumb_path)


@router.get('/collections/{collection_id}/archive/cover')
def collection_archive_cover(
    collection_id: int,
    request: Request,
    path: str,
    user: dict = Depends(get_current_user)
):
    collection = _get_collection_or_404(collection_id)
    _require_collection_token(collection, request, user)
    allowed = user.get('allowed_paths', [])
    if user.get('is_admin'):
        allowed = ['']
    if not allowed:
        raise HTTPException(status_code=403, detail='未配置可访问目录')

    rel_path = _normalize_path_for_listing(path)
    collection_paths = _normalize_paths_for_listing(collection['paths'])
    allowed_norm = _normalize_paths_for_listing(allowed)
    if not is_within_allowed(rel_path, collection_paths):
        raise HTTPException(status_code=403, detail='不在集合路径内')
    if '' not in allowed_norm and not is_within_allowed(rel_path, allowed_norm):
        raise HTTPException(status_code=403, detail='无权限访问')

    abs_path = resolve_any_path(settings.photo_root, rel_path)
    try:
        cover_file = get_archive_cover_file(abs_path)
        if not cover_file:
            raise HTTPException(status_code=404, detail='压缩包内未找到图片')
        thumb_path = get_archive_thumbnail(abs_path, cover_file, settings.thumb_cache, settings.thumb_size)
    except ArchiveSupportError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='压缩包内未找到图片')
    return FileResponse(thumb_path)
