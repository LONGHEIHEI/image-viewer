from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from app.services import db
from app.services.auth import hash_password
from app.services.deps import require_admin, get_current_user

router = APIRouter()


class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False
    allowed_paths: List[str] = []


class UserUpdate(BaseModel):
    password: str | None = None
    is_admin: bool | None = None
    allowed_paths: List[str] | None = None


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
    if db.get_user_by_username(payload.username):
        raise HTTPException(status_code=400, detail='用户名已存在')
    db.create_user(payload.username, hash_password(payload.password), payload.is_admin, payload.allowed_paths)
    return {'status': 'ok'}


@router.put('/users/{user_id}', dependencies=[Depends(require_admin)])
def update_user(user_id: int, payload: UserUpdate):
    if not db.get_user_by_id(user_id):
        raise HTTPException(status_code=404, detail='用户不存在')
    password_hash = hash_password(payload.password) if payload.password else None
    db.update_user(user_id, password_hash=password_hash, is_admin=payload.is_admin, allowed_paths=payload.allowed_paths)
    return {'status': 'ok'}


@router.delete('/users/{user_id}', dependencies=[Depends(require_admin)])
def delete_user(user_id: int):
    if not db.get_user_by_id(user_id):
        raise HTTPException(status_code=404, detail='用户不存在')
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
