from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import db
from app.services.auth import verify_password, create_access_token

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str


@router.post('/auth/login')
def login(payload: LoginRequest):
    user = db.get_user_by_username(payload.username)
    if not user or not verify_password(payload.password, user['password_hash']):
        raise HTTPException(status_code=401, detail='用户名或密码错误')
    token = create_access_token(user['username'])
    return {
        'access_token': token,
        'token_type': 'bearer',
        'user': {
            'id': user['id'],
            'username': user['username'],
            'is_admin': user['is_admin'],
            'allowed_paths': user['allowed_paths']
        }
    }
