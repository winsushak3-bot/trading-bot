import os
import uuid
import pathlib
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import aiofiles

from backend.api.schemas import UploadResponse
from backend.core.deps import get_admin_user_id

router = APIRouter()

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".webm"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/admin/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    _admin_id: int = Depends(get_admin_user_id),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename")

    # Безопасное извлечение расширения через pathlib
    ext = pathlib.PurePosixPath(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {ext} not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10 MB)")

    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # Защита от path traversal: убедиться что путь внутри UPLOAD_DIR
    filepath = os.path.abspath(filepath)
    if not filepath.startswith(UPLOAD_DIR):
        raise HTTPException(status_code=400, detail="Invalid file path")

    # Async запись файла (не блокирует event loop)
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(contents)

    return UploadResponse(url=f"/uploads/{filename}")
