from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth import decode_token
from app.services import db

_security = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_security)
):
    token = credentials.credentials if credentials else None
    if not token:
        token = request.query_params.get('token')
    if not token:
        raise HTTPException(status_code=401, detail='缺少登录凭证')

    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail='登录凭证无效')

    username = payload.get('sub')
    if not username:
        raise HTTPException(status_code=401, detail='登录凭证无效')

    user = db.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=401, detail='用户不存在')

    return user


def require_admin(user: dict = Depends(get_current_user)):
    if not user.get('is_admin'):
        raise HTTPException(status_code=403, detail='需要管理员权限')
    return user
