import zipfile
from pathlib import Path
from PIL import ImageFile
from app.utils.mime import guess_mime
from app.utils.path import to_relative

try:
    import py7zr
except ImportError:
    py7zr = None

try:
    import rarfile
except ImportError:
    rarfile = None

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}


class ArchiveSupportError(Exception):
    pass


def _read_image_dimensions_from_stream(stream) -> dict[str, int]:
    parser = ImageFile.Parser()
    try:
        while True:
            chunk = stream.read(64 * 1024)
            if not chunk:
                break
            parser.feed(chunk)
            if parser.image:
                width, height = parser.image.size
                if width > 0 and height > 0:
                    return {
                        'width': width,
                        'height': height
                    }
                break
    except Exception:
        return {}
    finally:
        try:
            parser.close()
        except Exception:
            pass
    return {}


def _build_archive_image_item(name: str, dimensions: dict[str, int]) -> dict:
    return {
        'name': Path(name).name,
        'path': name,
        **dimensions
    }


def _list_zip_image_items(path: Path, names: list[str]) -> list[dict]:
    items: list[dict] = []
    with zipfile.ZipFile(path, 'r') as zf:
        for name in names:
            dimensions = {}
            try:
                with zf.open(name, 'r') as fp:
                    dimensions = _read_image_dimensions_from_stream(fp)
            except Exception:
                dimensions = {}
            items.append(_build_archive_image_item(name, dimensions))
    return items


def _list_7z_image_items(path: Path, names: list[str]) -> list[dict]:
    if py7zr is None:
        raise ArchiveSupportError('需要安装 py7zr 才能支持 7z')
    items: list[dict] = []
    with py7zr.SevenZipFile(path, 'r') as zf:
        try:
            contents = zf.read(targets=names)
        except TypeError:
            contents = zf.read(names)
    for name in names:
        dimensions = {}
        handle = contents.get(name)
        if handle is not None:
            try:
                dimensions = _read_image_dimensions_from_stream(handle)
            except Exception:
                dimensions = {}
        items.append(_build_archive_image_item(name, dimensions))
    return items


def _list_rar_image_items(path: Path, names: list[str]) -> list[dict]:
    if rarfile is None:
        raise ArchiveSupportError('需要安装 rarfile 和 unrar 才能支持 RAR')
    items: list[dict] = []
    try:
        with rarfile.RarFile(path) as rf:
            for name in names:
                dimensions = {}
                try:
                    with rf.open(name) as fp:
                        dimensions = _read_image_dimensions_from_stream(fp)
                except Exception:
                    dimensions = {}
                items.append(_build_archive_image_item(name, dimensions))
    except rarfile.Error as exc:
        raise ArchiveSupportError(str(exc))
    return items


def _list_archive_image_items(path: Path, archive_type: str, names: list[str]) -> list[dict]:
    if archive_type == 'zip':
        return _list_zip_image_items(path, names)
    if archive_type == '7z':
        return _list_7z_image_items(path, names)
    return _list_rar_image_items(path, names)


def _list_zip(path: Path):
    files = []
    with zipfile.ZipFile(path, 'r') as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            files.append(info.filename)
    return files


def _read_zip(path: Path, file_path: str):
    with zipfile.ZipFile(path, 'r') as zf:
        with zf.open(file_path, 'r') as fp:
            return fp.read()


def _list_7z(path: Path):
    if py7zr is None:
        raise ArchiveSupportError('需要安装 py7zr 才能支持 7z')
    with py7zr.SevenZipFile(path, 'r') as zf:
        return zf.getnames()


def _read_7z(path: Path, file_path: str):
    if py7zr is None:
        raise ArchiveSupportError('需要安装 py7zr 才能支持 7z')
    with py7zr.SevenZipFile(path, 'r') as zf:
        try:
            contents = zf.read(targets=[file_path])
        except TypeError:
            contents = zf.read([file_path])
    if file_path not in contents:
        raise KeyError(file_path)
    return contents[file_path].read()


def _list_rar(path: Path):
    if rarfile is None:
        raise ArchiveSupportError('需要安装 rarfile 和 unrar 才能支持 RAR')
    try:
        with rarfile.RarFile(path) as rf:
            return [info.filename for info in rf.infolist() if not info.is_dir()]
    except rarfile.Error as exc:
        raise ArchiveSupportError(str(exc))


def _read_rar(path: Path, file_path: str):
    if rarfile is None:
        raise ArchiveSupportError('需要安装 rarfile 和 unrar 才能支持 RAR')
    try:
        with rarfile.RarFile(path) as rf:
            with rf.open(file_path) as fp:
                return fp.read()
    except rarfile.Error as exc:
        raise ArchiveSupportError(str(exc))


def _archive_type(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == '.zip':
        return 'zip'
    if ext == '.7z':
        return '7z'
    if ext == '.rar':
        return 'rar'
    raise ArchiveSupportError('不支持的压缩格式')


def list_archive(archive_path: str, root: str, page: int = 1, page_size: int = 20):
    path = Path(archive_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f'Archive not found: {archive_path}')

    archive_type = _archive_type(path)
    if archive_type == 'zip':
        names = _list_zip(path)
    elif archive_type == '7z':
        names = _list_7z(path)
    else:
        names = _list_rar(path)

    image_names = [
        name for name in names
        if Path(name).suffix.lower() in IMAGE_EXTS
    ]
    image_names.sort(key=lambda item: item.lower())
    total_files = len(image_names)
    start = (page - 1) * page_size
    end = start + page_size
    files = _list_archive_image_items(path, archive_type, image_names[start:end])

    return {
        'archive': to_relative(path, root),
        'files': files,
        'page': page,
        'page_size': page_size,
        'total_files': total_files,
        'has_more': end < total_files
    }


def get_archive_cover_file(archive_path: str) -> str | None:
    path = Path(archive_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f'Archive not found: {archive_path}')

    archive_type = _archive_type(path)
    if archive_type == 'zip':
        names = _list_zip(path)
    elif archive_type == '7z':
        names = _list_7z(path)
    else:
        names = _list_rar(path)

    image_names = [
        name for name in names
        if Path(name).suffix.lower() in IMAGE_EXTS
    ]
    if not image_names:
        return None
    image_names.sort(key=lambda item: item.lower())
    return image_names[0]


def stream_archive_image(archive_path: str, file_path: str):
    path = Path(archive_path)
    if not path.exists() or not path.is_file():
        return None, None

    archive_type = _archive_type(path)
    try:
        if archive_type == 'zip':
            data = _read_zip(path, file_path)
        elif archive_type == '7z':
            data = _read_7z(path, file_path)
        else:
            data = _read_rar(path, file_path)
    except KeyError:
        return None, None

    return data, guess_mime(file_path)
