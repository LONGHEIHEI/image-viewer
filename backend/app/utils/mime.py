import mimetypes


def guess_mime(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    return mime or 'application/octet-stream'
