from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.database.database import get_db

from app.auth.dependencies import get_current_user
from app.auth.rbac import require_role

from app.models.user import User

from app.services.file_service import (
    save_file,
    import_products_from_excel,
    UPLOAD_FOLDER
)

from app.services.activity_service import create_activity

router = APIRouter(
    prefix="/files",
    tags=["Files"]
)


# ---------------------------------
# Upload File
# ---------------------------------

@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    require_role(
        user,
        ["admin", "manager"]
    )

    file_path = save_file(file)

    count = import_products_from_excel(
        file_path,
        db
    )

    logged_user = (
        db.query(User)
        .filter(User.id == user["user_id"])
        .first()
    )

    if logged_user:
        create_activity(
            db=db,
            module="Files",
            action="Upload",
            description=f"Uploaded {file.filename} ({count} products)",
            username=logged_user.username
        )

    return {
        "message": "File uploaded and products imported successfully",
        "filename": file.filename,
        "products_added": count
    }


# ---------------------------------
# Download File
# ---------------------------------

@router.get("/{filename}")
def download_file(
    filename: str,
    user=Depends(get_current_user)
):

    require_role(
        user,
        ["admin", "manager", "viewer"]
    )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    return FileResponse(
        path=file_path,
        filename=filename
    )