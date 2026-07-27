from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List
from app.services import db
from app.services.auth import hash_password
from app.services.deps import require_admin, get_current_user

router = APIRouter()

USERNAME_MIN_LEN = 2
USERNAME_MAX_LEN = 32
PASSWORD_MIN_LEN = 6


class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False
    allowed_paths: List[str] = Field(default_factory=list)


class UserUpdate(BaseModel):
    password: str | None = None
    is_admin: bool | None = None
    allowed_paths: List[str] | None = None


def normalize_allowed_paths(paths: List[str] | None) -> List[str]:
    if not paths:
        return []
    # Trim, drop empties, de-dupe while preserving order.
    seen = set()
    out: List[str] = []
    for raw in paths:
        if not isinstance(raw, str):
            continue
        value = raw.strip()
        if not value:
            continue
        if value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


@router.get('/users', dependencies=[Depends(require_admin)])
def list_all_users():
    users = db.list_users()
    return [
        {
            'id': u['id'],
            'username': u['username'],
            'is_admin': u['is_admin'],
            'allowed_paths': u['allowed_paths'],
            'created_at': u['created_at']
        }
        for u in users
    ]


@router.post('/users', dependencies=[Depends(require_admin)])
def create_user(payload: UserCreate):
    username = (payload.username or '').strip()
    if len(username) < USERNAME_MIN_LEN or len(username) > USERNAME_MAX_LEN:
        raise HTTPException(status_code=400, detail=f'用户名长度需为 {USERNAME_MIN_LEN}-{USERNAME_MAX_LEN} 个字符')
    if len(payload.password or '') < PASSWORD_MIN_LEN:
        raise HTTPException(status_code=400, detail=f'密码长度至少 {PASSWORD_MIN_LEN} 位')
    if db.get_user_by_username(username):
        raise HTTPException(status_code=400, detail='用户名已存在')
    db.create_user(username, hash_password(payload.password), payload.is_admin, normalize_allowed_paths(payload.allowed_paths))
    return {'status': 'ok'}


@router.put('/users/{user_id}', dependencies=[Depends(require_admin)])
def update_user(user_id: int, payload: UserUpdate, current_user: dict = Depends(get_current_user)):
    target = db.get_user_by_id(user_id)
    if not target:
        raise HTTPException(status_code=404, detail='用户不存在')
    if payload.password is not None and payload.password != '' and len(payload.password) < PASSWORD_MIN_LEN:
        raise HTTPException(status_code=400, detail=f'密码长度至少 {PASSWORD_MIN_LEN} 位')
    if payload.is_admin is False and int(current_user.get('id') or 0) == int(user_id):
        raise HTTPException(status_code=400, detail='不能取消自己的管理员权限')
    if payload.is_admin is False and bool(target.get('is_admin')):
        if db.count_admins() <= 1:
            raise HTTPException(status_code=400, detail='系统至少需要保留 1 个管理员账号')
    password_hash = hash_password(payload.password) if payload.password else None
    db.update_user(
        user_id,
        password_hash=password_hash,
        is_admin=payload.is_admin,
        allowed_paths=normalize_allowed_paths(payload.allowed_paths) if payload.allowed_paths is not None else None
    )
    return {'status': 'ok'}


@router.delete('/users/{user_id}', dependencies=[Depends(require_admin)])
def delete_user(user_id: int, current_user: dict = Depends(get_current_user)):
    target = db.get_user_by_id(user_id)
    if not target:
        raise HTTPException(status_code=404, detail='用户不存在')
    if int(current_user.get('id') or 0) == int(user_id):
        raise HTTPException(status_code=400, detail='不能删除当前登录账号')
    if bool(target.get('is_admin')) and db.count_admins() <= 1:
        raise HTTPException(status_code=400, detail='系统至少需要保留 1 个管理员账号')
    db.delete_user(user_id)
    return {'status': 'ok'}


@router.get('/auth/me')
def me(user: dict = Depends(get_current_user)):
    return {
        'id': user['id'],
        'username': user['username'],
        'is_admin': user['is_admin'],
        'allowed_paths': user['allowed_paths']
    }
