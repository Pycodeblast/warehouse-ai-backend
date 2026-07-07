from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os

from app.auth.dependencies import get_current_user
from app.auth.rbac import require_role
from app.services.file_service import save_file, UPLOAD_FOLDER

router = APIRouter(
    prefix="/files",
    tags=["Files"]
)


@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    require_role(user, ["admin", "manager"])

    filename = save_file(file)

    return {
        "message": "File uploaded successfully",
        "filename": filename
    }


@router.get("/{filename}")
def download_file(
    filename: str,
    user=Depends(get_current_user)
):
    require_role(user, ["admin", "manager", "viewer"])

    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    return FileResponse(
        path=file_path,
        filename=filename
    )