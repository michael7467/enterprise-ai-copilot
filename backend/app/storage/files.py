"""Uploaded files: stored under data/uploads/<file_id>/ with a small metadata file."""
import uuid
from pathlib import Path

from app.config import settings
from app.schemas import FileKind, UploadedFile

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}
DOCUMENT_EXT = {".pdf", ".txt", ".md"}   # .docx: not supported yet


class UnsupportedFileType(ValueError):
    pass


class FileTooLarge(ValueError):
    pass


def file_kind(filename: str) -> FileKind:
    ext = Path(filename).suffix.lower()
    if ext in IMAGE_EXT:
        return "image"
    if ext in DOCUMENT_EXT:
        return "document"
    raise UnsupportedFileType(f"Unsupported file type: {ext or 'none'}")


def save_upload(filename: str, data: bytes) -> tuple[UploadedFile, Path]:
    """Store the file; returns its metadata and the stored file's path."""
    safe_name = Path(filename).name or "upload"   # drop any folder parts: no path tricks
    kind = file_kind(safe_name)
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise FileTooLarge(f"File is larger than {settings.max_upload_mb} MB.")
    file_id = uuid.uuid4().hex
    folder = settings.upload_dir / file_id
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"original{Path(safe_name).suffix.lower()}"
    path.write_bytes(data)
    meta = UploadedFile(file_id=file_id, filename=safe_name, size=len(data), kind=kind)
    save_meta(meta)
    return meta, path


def save_meta(meta: UploadedFile) -> None:
    (settings.upload_dir / meta.file_id / "meta.json").write_text(meta.model_dump_json(), encoding="utf-8")


def get_upload(file_id: str) -> UploadedFile | None:
    if not file_id.isalnum():   # ids are hex: this blocks "../" and similar
        return None
    meta = settings.upload_dir / file_id / "meta.json"
    if not meta.exists():
        return None
    return UploadedFile.model_validate_json(meta.read_text(encoding="utf-8"))
