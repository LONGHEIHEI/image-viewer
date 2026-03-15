from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.responses import FileResponse, Response
import random
from pathlib import Path
from pydantic import BaseModel
from typing import List
from app.services import db
from app.services.auth import hash_password, verify_password, create_collection_token, decode_token
from app.services.deps import get_current_user, require_admin
from app.services.fs_indexer import list_folder, IMAGE_EXTS
from app.services.archive_reader import list_archive, stream_archive_image, ArchiveSupportError
from app.services.thumbnailer import get_thumbnail, get_archive_thumbnail
from app.config import Settings
from app.utils.path import (
    resolve_under_root,
    rel_from_abs,
    is_within_allowed,
    is_within_or_ancestor,
    normalize_rel
)

router = APIRouter()
settings = Settings()


class CollectionCreate(BaseModel):
    name: str
    paths: List[str]
    password: str | None = None


class CollectionUpdate(BaseModel):
    name: str | None = None
    paths: List[str] | None = None
    password: str | None = None
    clear_password: bool = False


class CollectionAccess(BaseModel):
    password: str | None = None


def _normalize_paths(paths: List[str]) -> List[str]:
    cleaned: List[str] = []
    for path in paths:
        norm = normalize_rel(path)
        if not norm:
            continue
        if norm not in cleaned:
            cleaned.append(norm)
    return cleaned


def _collection_accessible(collection_paths: List[str], user_allowed: List[str]) -> bool:
    if not user_allowed or '' in [normalize_rel(p) for p in user_allowed]:
        return True
    for path in collection_paths:
        if is_within_allowed(path, user_allowed) or is_within_or_ancestor(path, user_allowed):
            return True
    return False


def _get_collection_or_404(collection_id: int) -> dict:
    collection = db.get_collection_by_id(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail='集合不存在')
    return collection


def _require_collection_token(collection: dict, request: Request):
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


@router.get('/collections/available')
def list_collections_available(user: dict = Depends(get_current_user)):
    collections = db.list_collections()
    allowed = user.get('allowed_paths', [])
    if user.get('is_admin'):
        return [
            {
                'id': c['id'],
                'name': c['name'],
                'requires_password': bool(c.get('password_hash'))
            }
            for c in collections
        ]
    return [
        {
            'id': c['id'],
            'name': c['name'],
            'requires_password': bool(c.get('password_hash'))
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
        'requires_password': bool(collection.get('password_hash'))
    }


@router.post('/collections', dependencies=[Depends(require_admin)])
def create_collection(payload: CollectionCreate):
    if db.get_collection_by_name(payload.name):
        raise HTTPException(status_code=400, detail='集合名称已存在')
    paths = _normalize_paths(payload.paths)
    if not paths:
        raise HTTPException(status_code=400, detail='集合路径不能为空')
    password_hash = hash_password(payload.password) if payload.password else None
    db.create_collection(payload.name, paths, password_hash)
    return {'status': 'ok'}


@router.put('/collections/{collection_id}', dependencies=[Depends(require_admin)])
def update_collection(collection_id: int, payload: CollectionUpdate):
    if not db.get_collection_by_id(collection_id):
        raise HTTPException(status_code=404, detail='集合不存在')
    paths = _normalize_paths(payload.paths) if payload.paths is not None else None
    password_hash = hash_password(payload.password) if payload.password else None
    db.update_collection(
        collection_id,
        name=payload.name,
        paths=paths,
        password_hash=password_hash,
        clear_password=payload.clear_password
    )
    return {'status': 'ok'}


@router.delete('/collections/{collection_id}', dependencies=[Depends(require_admin)])
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


@router.get('/collections/{collection_id}/folder')
def collection_folder(
    collection_id: int,
    request: Request,
    path: str = Query(default=''),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=500),
    user: dict = Depends(get_current_user)
):
    collection = _get_collection_or_404(collection_id)
    _require_collection_token(collection, request)
    allowed = user.get('allowed_paths', [])
    if user.get('is_admin'):
        allowed = ['']
    if not allowed:
        raise HTTPException(status_code=403, detail='未配置可访问目录')

    collection_paths = [normalize_rel(p) for p in collection['paths']]
    if path == '':
        listing = _collection_root_listing(collection_paths)
        listing = _filter_listing(listing, allowed)
        return listing

    rel_path = normalize_rel(path)
    if not is_within_or_ancestor(rel_path, collection_paths):
        raise HTTPException(status_code=403, detail='不在集合路径内')
    if not is_within_or_ancestor(rel_path, allowed):
        raise HTTPException(status_code=403, detail='无权限访问')

    abs_path = resolve_under_root(settings.photo_root, rel_path)
    try:
        listing = list_folder(abs_path, settings.photo_root, page=page, page_size=page_size)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='目录不存在，请检查路径')
    listing = _filter_listing(listing, collection_paths)
    listing = _filter_listing(listing, allowed)
    return listing


@router.get('/collections/{collection_id}/folder/cover')
def collection_folder_cover(
    collection_id: int,
    request: Request,
    path: str,
    user: dict = Depends(get_current_user)
):
    collection = _get_collection_or_404(collection_id)
    _require_collection_token(collection, request)
    allowed = user.get('allowed_paths', [])
    if user.get('is_admin'):
        allowed = ['']
    if not allowed:
        raise HTTPException(status_code=403, detail='未配置可访问目录')

    rel_path = normalize_rel(path)
    collection_paths = [normalize_rel(p) for p in collection['paths']]
    if not is_within_or_ancestor(rel_path, collection_paths):
        raise HTTPException(status_code=403, detail='不在集合路径内')
    if not is_within_or_ancestor(rel_path, allowed):
        raise HTTPException(status_code=403, detail='无权限访问')

    abs_path = resolve_under_root(settings.photo_root, rel_path)
    try:
        image_path = _random_image_in_folder(abs_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='目录不存在，请检查路径')
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
    _require_collection_token(collection, request)
    allowed = user.get('allowed_paths', [])
    if user.get('is_admin'):
        allowed = ['']
    if not allowed:
        raise HTTPException(status_code=403, detail='未配置可访问目录')

    rel_path = normalize_rel(path)
    collection_paths = [normalize_rel(p) for p in collection['paths']]
    if not is_within_allowed(rel_path, collection_paths):
        raise HTTPException(status_code=403, detail='不在集合路径内')
    if not is_within_allowed(rel_path, allowed):
        raise HTTPException(status_code=403, detail='无权限访问')

    abs_path = resolve_under_root(settings.photo_root, rel_path)
    try:
        return list_archive(abs_path, settings.photo_root, page=page, page_size=page_size)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='压缩包不存在，请检查路径')
    except ArchiveSupportError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get('/collections/{collection_id}/image')
def collection_image(collection_id: int, path: str, request: Request, user: dict = Depends(get_current_user)):
    collection = _get_collection_or_404(collection_id)
    _require_collection_token(collection, request)
    allowed = user.get('allowed_paths', [])
    if user.get('is_admin'):
        allowed = ['']
    if not allowed:
        raise HTTPException(status_code=403, detail='未配置可访问目录')

    rel_path = normalize_rel(path)
    collection_paths = [normalize_rel(p) for p in collection['paths']]
    if not is_within_allowed(rel_path, collection_paths):
        raise HTTPException(status_code=403, detail='不在集合路径内')
    if not is_within_allowed(rel_path, allowed):
        raise HTTPException(status_code=403, detail='无权限访问')

    abs_path = resolve_under_root(settings.photo_root, rel_path)
    return FileResponse(abs_path)


@router.get('/collections/{collection_id}/thumb')
def collection_thumb(collection_id: int, path: str, request: Request, user: dict = Depends(get_current_user)):
    collection = _get_collection_or_404(collection_id)
    _require_collection_token(collection, request)
    allowed = user.get('allowed_paths', [])
    if user.get('is_admin'):
        allowed = ['']
    if not allowed:
        raise HTTPException(status_code=403, detail='未配置可访问目录')

    rel_path = normalize_rel(path)
    collection_paths = [normalize_rel(p) for p in collection['paths']]
    if not is_within_allowed(rel_path, collection_paths):
        raise HTTPException(status_code=403, detail='不在集合路径内')
    if not is_within_allowed(rel_path, allowed):
        raise HTTPException(status_code=403, detail='无权限访问')

    abs_path = resolve_under_root(settings.photo_root, rel_path)
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
    _require_collection_token(collection, request)
    allowed = user.get('allowed_paths', [])
    if user.get('is_admin'):
        allowed = ['']
    if not allowed:
        raise HTTPException(status_code=403, detail='未配置可访问目录')

    rel_path = normalize_rel(path)
    collection_paths = [normalize_rel(p) for p in collection['paths']]
    if not is_within_allowed(rel_path, collection_paths):
        raise HTTPException(status_code=403, detail='不在集合路径内')
    if not is_within_allowed(rel_path, allowed):
        raise HTTPException(status_code=403, detail='无权限访问')

    abs_path = resolve_under_root(settings.photo_root, rel_path)
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
    _require_collection_token(collection, request)
    allowed = user.get('allowed_paths', [])
    if user.get('is_admin'):
        allowed = ['']
    if not allowed:
        raise HTTPException(status_code=403, detail='未配置可访问目录')

    rel_path = normalize_rel(path)
    collection_paths = [normalize_rel(p) for p in collection['paths']]
    if not is_within_allowed(rel_path, collection_paths):
        raise HTTPException(status_code=403, detail='不在集合路径内')
    if not is_within_allowed(rel_path, allowed):
        raise HTTPException(status_code=403, detail='无权限访问')

    abs_path = resolve_under_root(settings.photo_root, rel_path)
    try:
        thumb_path = get_archive_thumbnail(abs_path, file, settings.thumb_cache, settings.thumb_size)
    except ArchiveSupportError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='压缩包内未找到图片')
    return FileResponse(thumb_path)
