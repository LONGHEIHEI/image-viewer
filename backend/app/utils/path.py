from pathlib import Path


def resolve_under_root(root: str, subpath: str) -> str:
    root_path = Path(root).resolve()
    target = (root_path / subpath).resolve()

    if root_path == target or root_path in target.parents:
        return str(target)

    raise ValueError('Invalid path')


def to_relative(path: Path, root: str) -> str:
    root_path = Path(root).resolve()
    try:
        return str(Path(path).resolve().relative_to(root_path))
    except ValueError:
        return str(path)


def normalize_rel(path: str) -> str:
    normalized = path.replace('\\', '/').strip('/')
    return normalized


def rel_from_abs(abs_path: str, root: str) -> str:
    rel = to_relative(Path(abs_path), root)
    return normalize_rel(rel)


def is_within_allowed(path: str, allowed_paths: list[str]) -> bool:
    if not allowed_paths:
        return True
    for allowed in allowed_paths:
        allowed_norm = normalize_rel(allowed)
        if allowed_norm == '':
            return True
        if path == allowed_norm or path.startswith(f'{allowed_norm}/'):
            return True
    return False


def is_within_or_ancestor(path: str, allowed_paths: list[str]) -> bool:
    if not allowed_paths:
        return True
    for allowed in allowed_paths:
        allowed_norm = normalize_rel(allowed)
        if allowed_norm == '':
            return True
        if path == allowed_norm or path.startswith(f'{allowed_norm}/'):
            return True
        if allowed_norm.startswith(f'{path}/'):
            return True
    return False
