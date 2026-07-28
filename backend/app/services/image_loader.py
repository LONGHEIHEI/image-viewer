from pathlib import Path


def is_image(path: str) -> bool:
    return Path(path).suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
