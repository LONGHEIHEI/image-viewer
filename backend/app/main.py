from fastapi import FastAPI
from pathlib import Path
from app.api.routes import router as api_router
from app.config import Settings
from app.services.db import init_db
from app.services.auth import ensure_admin_user

settings = Settings()

app = FastAPI(title='轻图 API')
app.include_router(api_router, prefix='/api')

@app.on_event('startup')
def startup():
    Path(settings.photo_root).mkdir(parents=True, exist_ok=True)
    Path(settings.thumb_cache).mkdir(parents=True, exist_ok=True)
    Path(settings.db_path).resolve().parent.mkdir(parents=True, exist_ok=True)
    init_db()
    ensure_admin_user()

@app.get('/health')
def health():
    return {'status': 'ok'}
