from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    photo_root: str = 'photos'
    thumb_cache: str = 'cache'
    thumb_size: int = 320
    db_path: str = 'data/app.db'
    secret_key: str = 'dev-secret-change-me'
    access_token_expire_minutes: int = 720
    admin_username: str = 'admin'
    admin_password: str = 'admin'

    class Config:
        env_prefix = ''
        case_sensitive = False
