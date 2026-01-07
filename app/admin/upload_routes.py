import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.auth.utils import admin_required
from fastapi import Depends

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/admin/upload", tags=["Admin - Uploads"])

@router.post("")
async def upload_image(file: UploadFile = File(...), user=Depends(admin_required)):
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        raise HTTPException(400, "Invalid image format")

    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    return JSONResponse({"image_url": f"/uploads/{filename}"})

