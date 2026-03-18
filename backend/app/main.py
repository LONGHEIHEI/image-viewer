from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from app.config import Settings
from app.services import db

settings = Settings()
app = FastAPI(title='Image Views')


def _include_api_routers() -> None:
    import app.api as api_pkg

    for module_info in pkgutil.iter_modules(api_pkg.__path__):
        if module_info.name.startswith('_'):
            continue
        module = importlib.import_module(f'app.api.{module_info.name}')
        router = getattr(module, 'router', None)
        if router is None:
            continue
        app.include_router(router, prefix='/api')


def _resolve_frontend_dist() -> Path | None:
    # Keep both candidates for compatibility with local runs and docker image layout.
    candidates = [
        Path(__file__).resolve().parent / 'static',
        Path(__file__).resolve().parents[2] / 'frontend' / 'dist'
    ]
    for candidate in candidates:
        if (candidate / 'index.html').exists():
            return candidate
    return None


_include_api_routers()
_FRONTEND_DIST = _resolve_frontend_dist()


@app.on_event('startup')
def startup() -> None:
    photo_root = Path(settings.photo_root)
    thumb_cache_dir = Path(settings.thumb_cache)
    photo_root.mkdir(parents=True, exist_ok=True)
    thumb_cache_dir.mkdir(parents=True, exist_ok=True)
    db.init_db()


@app.get('/api/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}


@app.get('/health')
def health_compat() -> dict[str, str]:
    return {'status': 'ok'}


@app.get('/', include_in_schema=False)
def spa_root():
    if _FRONTEND_DIST is None:
        raise HTTPException(status_code=404, detail='Frontend not found')
    return FileResponse(_FRONTEND_DIST / 'index.html')


@app.get('/{full_path:path}', include_in_schema=False)
def spa_fallback(full_path: str):
    if _FRONTEND_DIST is None:
        raise HTTPException(status_code=404, detail='Not Found')

    if full_path.startswith('api/'):
        raise HTTPException(status_code=404, detail='Not Found')

    target = (_FRONTEND_DIST / full_path).resolve()
    dist_root = _FRONTEND_DIST.resolve()
    try:
        target.relative_to(dist_root)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail='Not Found') from exc

    if target.is_file():
        return FileResponse(target)

    return FileResponse(dist_root / 'index.html')
