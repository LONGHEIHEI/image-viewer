from fastapi import APIRouter
from app.api.images import router as images_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.collections import router as collections_router
from app.api.fs import router as fs_router

router = APIRouter()
router.include_router(auth_router, tags=['auth'])
router.include_router(users_router, tags=['users'])
router.include_router(collections_router, tags=['collections'])
router.include_router(images_router, tags=['images'])
router.include_router(fs_router, tags=['fs'])
