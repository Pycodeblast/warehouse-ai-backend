from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException,
)

from fastapi.responses import FileResponse
from fastapi import Body

import os
import tempfile
from datetime import datetime
import pandas as pd

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.product import Product

from app.auth.dependencies import get_current_user
from app.auth.rbac import require_role

from app.services.file_service import (
    save_file,
    list_files,
    delete_file,
    UPLOAD_FOLDER,
)

router = APIRouter(
    prefix="/files",
    tags=["Files"],
)


# -----------------------------------
# Upload File
# -----------------------------------

@router.post("/upload")
def upload_file(
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    require_role(
        user,
        ["admin", "manager"],
    )

    uploaded = save_file(db, file)

    return {
        "message": "File uploaded successfully.",
        "file": uploaded,
    }


# -----------------------------------
# List Uploaded Files
# -----------------------------------

@router.get("/")
def get_files(
    user=Depends(get_current_user),
):
    require_role(
        user,
        ["admin", "manager", "viewer"],
    )

    return list_files()


# -----------------------------------
# Export Products
# -----------------------------------

@router.post("/export")
def export_products(
    products:  list = Body(...),
    user=Depends(get_current_user),
):
    require_role(
        user,
        ["admin", "manager"],
    )

    df = pd.DataFrame(products)

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".xlsx",
    )

    df.to_excel(
        temp_file.name,
        index=False,
    )

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    filename = f"Product_List_{current_time}.xlsx"

    return FileResponse(
        path=temp_file.name,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# -----------------------------------
# Download Uploaded File
# -----------------------------------

@router.get("/download/{filename}")
def download_file(
    filename: str,
    user=Depends(get_current_user),
):
    require_role(
        user,
        ["admin", "manager", "viewer"],
    )

    path = os.path.join(
        UPLOAD_FOLDER,
        filename,
    )

    if not os.path.exists(path):
        raise HTTPException(
            status_code=404,
            detail="File not found.",
        )

    return FileResponse(
        path=path,
        filename=filename,
        media_type="application/octet-stream",
    )


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