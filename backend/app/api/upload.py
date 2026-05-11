import os
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends
from app.config import get_settings
from app.dependencies import get_current_user
from app.utils.response import success
from app.utils.exceptions import BadRequestException

settings = get_settings()
upload_router = APIRouter(tags=["文件上传"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_FILE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "application/pdf"}


@upload_router.post("/upload/image")
async def upload_image(file: UploadFile = File(...), user=Depends(get_current_user)):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise BadRequestException("仅支持 JPG/PNG/GIF/WebP 图片格式")
    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise BadRequestException("文件大小不能超过 10MB")

    ext = os.path.splitext(file.filename or ".jpg")[1] or ".jpg"
    today = datetime.now().strftime("%Y%m%d")
    relative_path = f"images/{today}/{uuid.uuid4().hex}{ext}"
    full_path = os.path.join(settings.UPLOAD_DIR, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    content = await file.read()
    with open(full_path, "wb") as f:
        f.write(content)

    return success({"url": f"/uploads/{relative_path}", "name": file.filename})


@upload_router.post("/upload/file")
async def upload_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise BadRequestException("仅支持 JPG/PNG/GIF/WebP/PDF 格式")
    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise BadRequestException("文件大小不能超过 10MB")

    ext = os.path.splitext(file.filename or ".pdf")[1] or ".pdf"
    today = datetime.now().strftime("%Y%m%d")
    relative_path = f"files/{today}/{uuid.uuid4().hex}{ext}"
    full_path = os.path.join(settings.UPLOAD_DIR, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    content = await file.read()
    with open(full_path, "wb") as f:
        f.write(content)

    return success({"url": f"/uploads/{relative_path}", "name": file.filename})
