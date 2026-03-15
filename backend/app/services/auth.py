from datetime import datetime, timedelta, timezone
import hashlib
from passlib.context import CryptContext
import jwt
from app.config import Settings
from app.services import db

settings = Settings()
_pwd = CryptContext(schemes=['bcrypt'], deprecated='auto')


def _normalize_password(password: str) -> str:
    # bcrypt only supports up to 72 bytes, pre-hash if longer
    if len(password.encode('utf-8')) <= 72:
        return password
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def hash_password(password: str) -> str:
    return _pwd.hash(_normalize_password(password))


def verify_password(password: str, hashed: str) -> bool:
    return _pwd.verify(_normalize_password(password), hashed)


def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        'sub': username,
        'exp': expire
    }
    return jwt.encode(payload, settings.secret_key, algorithm='HS256')


def decode_token(token: str):
    return jwt.decode(token, settings.secret_key, algorithms=['HS256'])


def ensure_admin_user():
    if db.get_user_by_username(settings.admin_username):
        return
    db.create_user(
        settings.admin_username,
        hash_password(settings.admin_password),
        True,
        ['']
    )
