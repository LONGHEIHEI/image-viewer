from fastapi import APIRouter, Depends, HTTPException, Query
from pathlib import Path
import os
import string
from app.services.deps import require_admin
from app.utils.path import normalize_path

router = APIRouter()


def _format_path(path: Path) -> str:
    return normalize_path(str(path))


def _list_roots() -> list[dict]:
    if os.name == 'nt':
        roots = []
        for letter in string.ascii_uppercase:
            drive = Path(f'{letter}:/')
            if drive.exists():
                roots.append({'name': f'{letter}:', 'path': _format_path(drive)})
        return roots
    return [{'name': '/', 'path': '/'}]


@router.get('/fs/roots', dependencies=[Depends(require_admin)])
def list_roots():
    return {'roots': _list_roots()}


@router.get('/fs/list', dependencies=[Depends(require_admin)])
def list_folders(path: str = Query(...)):
    target = Path(path)
    if not target.exists():
        raise HTTPException(status_code=404, detail='目录不存在')
    if not target.is_dir():
        raise HTTPException(status_code=400, detail='路径不是目录')

    try:
        entries = list(target.iterdir())
    except PermissionError:
        raise HTTPException(status_code=403, detail='无权限访问该目录')

    folders = []
    for entry in sorted(entries, key=lambda p: p.name.lower()):
        if entry.is_dir():
            folders.append({'name': entry.name, 'path': _format_path(entry.resolve())})

    parent = ''
    if target.parent != target:
        parent = _format_path(target.parent.resolve())

    return {
        'path': _format_path(target.resolve()),
        'parent': parent,
        'folders': folders
    }
