from fastapi import FastAPI
from app.api.routes import router as api_router
from app.config import Settings
from app.services.db import init_db
from app.services.auth import ensure_admin_user

settings = Settings()

app = FastAPI(title='Image Views API')
app.include_router(api_router, prefix='/api')

@app.on_event('startup')
def startup():
    init_db()
    ensure_admin_user()

@app.get('/health')
def health():
    return {'status': 'ok'}
