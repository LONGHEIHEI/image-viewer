from pydantic_settings import BaseSettings
import logging

logger = logging.getLogger(__name__)

_DEFAULT_SECRET = 'dev-secret-change-me'


class Settings(BaseSettings):
    photo_root: str = 'photos'
    thumb_cache: str = 'cache'
    thumb_cache_max_mb: int = 500
    thumb_size: int = 320
    db_path: str = 'data/app.db'
    secret_key: str = _DEFAULT_SECRET
    access_token_expire_minutes: int = 720
    admin_username: str = 'admin'
    admin_password: str = 'admin'

    class Config:
        env_prefix = ''
        case_sensitive = False

    def check_secret_key(self) -> None:
        if self.secret_key == _DEFAULT_SECRET:
            import secrets
            generated = secrets.token_hex(32)
            logger.critical(
                '!!! 安全警告: SECRET_KEY 仍为默认值，JWT 可被外部伪造。'
                '请立即通过环境变量 SECRET_KEY 设置强密钥，例如: '
                f'SECRET_KEY={generated}'
            )
