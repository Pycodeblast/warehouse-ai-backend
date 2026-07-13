from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException,
)

from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import tempfile
from datetime import datetime
import pandas as pd

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.product import Product

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
from app.services.storage.local_storage import LocalStorage
from fastapi.responses import RedirectResponse
from app.services.storage.s3_storage import S3Storage
from app.models.uploaded_file import UploadedFile

router = APIRouter(
    prefix="/files",
    tags=["Files"],
)


# ---------------------------------
# Upload File
# ---------------------------------

@router.post("/upload")
def upload_file(
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    require_role(
        user,
        ["admin", "manager"]
    )

    # Initialize storage
    local_storage = LocalStorage()
    s3_storage = S3Storage()

    # Step 1: Save temporarily in local storage
    local_path = local_storage.upload(file)

    # Step 2: Import products from Excel
    result = import_products_from_excel(
        local_path,
        db
    )

    # Step 3: Upload to S3
    file.file.seek(0)   # Reset file pointer
    s3_key = s3_storage.upload(file)

    # Step 4: Save metadata
    logged_user = (
        db.query(User)
        .filter(User.id == user["user_id"])
        .first()
    )

    uploaded_file = UploadedFile(
    original_name=file.filename,
    storage_key=s3_key,
    storage_type="s3",
    uploaded_by=logged_user.username if logged_user else "Unknown"
)

    db.add(uploaded_file)
    db.commit()

    # Step 5: Activity log
    if logged_user:
        create_activity(
            db=db,
            module="Files",
            action="Upload",
            description=f"Uploaded {file.filename} ({result['imported']} products)",
            username=logged_user.username
        )

    # Step 6: Delete temporary file
    if os.path.exists(local_path):
        os.remove(local_path)
        
    return {
    "message": "File uploaded successfully",
    "file_id": uploaded_file.id,
    "filename": file.filename,
    "products_added": result["imported"],
    "products_skipped": result["skipped"],
    "duplicate_skus": result["duplicate_skus"],
    "storage": "S3",
    "storage_key": s3_key
}


# ---------------------------------
# List Uploaded Files
# ---------------------------------

@router.get("/")
def get_uploaded_files(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    require_role(
        user,
        ["admin", "manager", "viewer"]
    )

    files = (
        db.query(UploadedFile)
        .order_by(UploadedFile.uploaded_at.desc())
        .all()
    )

    return [
        {
            "id": file.id,
            "original_name": file.original_name,
            "uploaded_by": file.uploaded_by,
            "uploaded_at": file.uploaded_at,
            "storage_type": file.storage_type,
        }
        for file in files
    ]
# ---------------------------------
# Download File
# ---------------------------------
@router.get("/download/{file_id}")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    require_role(
        user,
        ["admin", "manager", "viewer"]
    )

    uploaded_file = (
        db.query(UploadedFile)
        .filter(UploadedFile.id == file_id)
        .first()
    )

    if not uploaded_file:
        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    s3 = S3Storage()

    download_url = s3.download(uploaded_file.storage_key)

    return {
    "download_url": download_url
}
# -----------------------------------
# Delete Uploaded File
# -----------------------------------

@router.delete("/{filename}")
def remove_file(
    filename: str,
    user=Depends(get_current_user),
):
    require_role(
        user,
        ["admin"],
    )

    return delete_file(filename) 