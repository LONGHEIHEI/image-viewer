from pathlib import Path


def is_abs_path(path: str) -> bool:
    try:
        return Path(path).is_absolute()
    except Exception:
        return False


def normalize_path(path: str) -> str:
    raw = path.replace('\\', '/').strip()
    if raw == '':
        return ''
    if raw == '.':
        return ''
    if is_abs_path(raw):
        normalized = raw.rstrip('/')
        if normalized == '' and raw.startswith('/'):
            return '/'
        if len(normalized) == 2 and normalized[1] == ':':
            normalized += '/'
        return normalized
    return raw.strip('/')


def resolve_under_root(root: str, subpath: str) -> str:
    root_path = Path(root).resolve()
    target = (root_path / subpath).resolve()

    if root_path == target or root_path in target.parents:
        return str(target)

    raise ValueError('Invalid path')


def resolve_any_path(root: str, subpath: str) -> str:
    if is_abs_path(subpath):
        return str(Path(subpath).resolve())
    return resolve_under_root(root, subpath)


def to_relative(path: Path, root: str) -> str:
    root_path = Path(root).resolve()
    try:
        return str(Path(path).resolve().relative_to(root_path))
    except ValueError:
        return str(path)


def normalize_rel(path: str) -> str:
    normalized = path.replace('\\', '/').strip('/')
    if normalized == '.':
        return ''
    return normalized


def rel_from_abs(abs_path: str, root: str) -> str:
    rel = to_relative(Path(abs_path), root)
    return normalize_rel(rel)


def is_within_allowed(path: str, allowed_paths: list[str]) -> bool:
    if not allowed_paths:
        return True
    path_norm = normalize_path(path)
    for allowed in allowed_paths:
        allowed_norm = normalize_path(allowed)
        if allowed_norm == '':
            return True
        if path_norm == allowed_norm or path_norm.startswith(f'{allowed_norm}/'):
            return True
    return False


def is_within_or_ancestor(path: str, allowed_paths: list[str]) -> bool:
    if not allowed_paths:
        return True
    path_norm = normalize_path(path)
    for allowed in allowed_paths:
        allowed_norm = normalize_path(allowed)
        if allowed_norm == '':
            return True
        if path_norm == allowed_norm or path_norm.startswith(f'{allowed_norm}/'):
            return True
        if allowed_norm.startswith(f'{path_norm}/'):
            return True
    return False
