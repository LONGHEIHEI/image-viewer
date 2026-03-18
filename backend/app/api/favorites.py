from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.collections import (
    _collection_accessible,
    _get_collection_or_404,
    _normalize_path_for_listing,
    _normalize_paths_for_listing
)
from app.api.images import require_allowed_paths, safe_resolve
from app.config import Settings
from app.services import db
from app.services.auth import decode_token
from app.services.deps import get_current_user
from app.utils.path import is_within_allowed, is_within_or_ancestor, normalize_path, rel_from_abs

router = APIRouter()
settings = Settings()

FAVORITE_SOURCE_KINDS = {
    'image',
    'archive_image',
    'collection_image',
    'collection_archive_image'
}


class FavoritePayload(BaseModel):
    source_kind: str
    collection_id: int | None = None
    container_path: str = ''
    item_path: str
    folder_path: str = ''
    view_mode: str = 'folder'
    item_name: str = ''
    collection_token: str | None = None


class FavoriteDeletePayload(BaseModel):
    source_kind: str
    collection_id: int | None = None
    container_path: str = ''
    item_path: str


def _validate_source_kind(source_kind: str) -> str:
    if source_kind not in FAVORITE_SOURCE_KINDS:
        raise HTTPException(status_code=400, detail='不支持的收藏类型')
    return source_kind


def _normalize_archive_item_path(path: str) -> str:
    normalized = normalize_path(path)
    if not normalized:
        raise HTTPException(status_code=400, detail='图片路径不能为空')
    return normalized


def _normalize_root_path(path: str) -> str:
    resolved = safe_resolve(path)
    return rel_from_abs(resolved, settings.photo_root)


def _normalize_view_mode(view_mode: str) -> str:
    return 'flat' if view_mode == 'flat' else 'folder'


def _normalize_identity(payload: FavoriteDeletePayload) -> dict:
    source_kind = _validate_source_kind(payload.source_kind)
    if source_kind in {'image', 'archive_image'}:
        container_path = _normalize_root_path(payload.container_path) if payload.container_path else ''
        item_path = (
            _normalize_archive_item_path(payload.item_path)
            if source_kind == 'archive_image'
            else _normalize_root_path(payload.item_path)
        )
        return {
            'source_kind': source_kind,
            'collection_id': None,
            'container_path': container_path,
            'item_path': item_path
        }

    if payload.collection_id is None:
        raise HTTPException(status_code=400, detail='缺少集合编号')

    container_path = _normalize_path_for_listing(payload.container_path) if payload.container_path else ''
    item_path = (
        _normalize_archive_item_path(payload.item_path)
        if source_kind == 'collection_archive_image'
        else _normalize_path_for_listing(payload.item_path)
    )
    return {
        'source_kind': source_kind,
        'collection_id': payload.collection_id,
        'container_path': container_path,
        'item_path': item_path
    }


def _require_collection_payload_access(collection: dict, token: str | None, user: dict) -> None:
    if user.get('is_admin'):
        return
    if not collection.get('password_hash'):
        return
    if not token:
        raise HTTPException(status_code=401, detail='集合需要密码')
    try:
        payload = decode_token(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail='集合访问凭证无效') from exc
    if payload.get('typ') != 'collection' or payload.get('cid') != collection['id']:
        raise HTTPException(status_code=401, detail='集合访问凭证无效')


def _validate_favorite_payload(payload: FavoritePayload, user: dict) -> dict:
    source_kind = _validate_source_kind(payload.source_kind)
    item_name = payload.item_name.strip() or normalize_path(payload.item_path).split('/')[-1]
    view_mode = _normalize_view_mode(payload.view_mode)

    if source_kind == 'image':
        allowed = require_allowed_paths(user)
        item_path = _normalize_root_path(payload.item_path)
        if not is_within_allowed(item_path, allowed):
            raise HTTPException(status_code=403, detail='无权限访问')
        folder_path = _normalize_root_path(payload.folder_path) if payload.folder_path else ''
        if folder_path and not is_within_or_ancestor(folder_path, allowed):
            raise HTTPException(status_code=403, detail='无权限访问')
        return {
            'source_kind': source_kind,
            'collection_id': None,
            'container_path': '',
            'item_path': item_path,
            'folder_path': folder_path,
            'view_mode': view_mode,
            'item_name': item_name
        }

    if source_kind == 'archive_image':
        allowed = require_allowed_paths(user)
        container_path = _normalize_root_path(payload.container_path)
        if not is_within_allowed(container_path, allowed):
            raise HTTPException(status_code=403, detail='无权限访问')
        folder_path = _normalize_root_path(payload.folder_path) if payload.folder_path else ''
        if folder_path and not is_within_or_ancestor(folder_path, allowed):
            raise HTTPException(status_code=403, detail='无权限访问')
        return {
            'source_kind': source_kind,
            'collection_id': None,
            'container_path': container_path,
            'item_path': _normalize_archive_item_path(payload.item_path),
            'folder_path': folder_path,
            'view_mode': view_mode,
            'item_name': item_name
        }

    if payload.collection_id is None:
        raise HTTPException(status_code=400, detail='缺少集合编号')

    collection = _get_collection_or_404(payload.collection_id)
    user_allowed = user.get('allowed_paths', [])
    if not user.get('is_admin') and not user_allowed:
        raise HTTPException(status_code=403, detail='未配置可访问目录')
    if not user.get('is_admin') and not _collection_accessible(collection['paths'], user_allowed):
        raise HTTPException(status_code=403, detail='无权限访问该集合')
    _require_collection_payload_access(collection, payload.collection_token, user)

    collection_paths = _normalize_paths_for_listing(collection['paths'])
    allowed_paths = [''] if user.get('is_admin') else user_allowed
    allowed_norm = _normalize_paths_for_listing(allowed_paths) if allowed_paths else []
    allow_all = '' in allowed_norm
    folder_path = _normalize_path_for_listing(payload.folder_path) if payload.folder_path else ''
    if folder_path:
        if not is_within_or_ancestor(folder_path, collection_paths):
            raise HTTPException(status_code=403, detail='不在集合路径内')
        if not allow_all and allowed_norm and not is_within_or_ancestor(folder_path, allowed_norm):
            raise HTTPException(status_code=403, detail='无权限访问')

    if source_kind == 'collection_image':
        item_path = _normalize_path_for_listing(payload.item_path)
        if not is_within_allowed(item_path, collection_paths):
            raise HTTPException(status_code=403, detail='不在集合路径内')
        if not allow_all and allowed_norm and not is_within_allowed(item_path, allowed_norm):
            raise HTTPException(status_code=403, detail='无权限访问')
        return {
            'source_kind': source_kind,
            'collection_id': payload.collection_id,
            'container_path': '',
            'item_path': item_path,
            'folder_path': folder_path,
            'view_mode': view_mode,
            'item_name': item_name
        }

    container_path = _normalize_path_for_listing(payload.container_path)
    if not is_within_allowed(container_path, collection_paths):
        raise HTTPException(status_code=403, detail='不在集合路径内')
    if not allow_all and allowed_norm and not is_within_allowed(container_path, allowed_norm):
        raise HTTPException(status_code=403, detail='无权限访问')
    return {
        'source_kind': source_kind,
        'collection_id': payload.collection_id,
        'container_path': container_path,
        'item_path': _normalize_archive_item_path(payload.item_path),
        'folder_path': folder_path,
        'view_mode': view_mode,
        'item_name': item_name
    }


@router.get('/favorites')
def list_favorites(user: dict = Depends(get_current_user)):
    return db.list_favorites(user['id'])


@router.post('/favorites')
def create_favorite(payload: FavoritePayload, user: dict = Depends(get_current_user)):
    normalized = _validate_favorite_payload(payload, user)
    db.save_favorite(user['id'], **normalized)
    return {'status': 'ok'}


@router.delete('/favorites')
def delete_favorite(payload: FavoriteDeletePayload, user: dict = Depends(get_current_user)):
    normalized = _normalize_identity(payload)
    db.delete_favorite(user['id'], **normalized)
    return {'status': 'ok'}
