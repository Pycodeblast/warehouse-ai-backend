import os
import shutil

from .storage_interface import StorageInterface


UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class LocalStorage(StorageInterface):

    def upload(self, file):

        path = os.path.join(
            UPLOAD_FOLDER,
            file.filename
        )

        with open(path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        return path

    def download(self, key):
        pass

    def delete(self, key):
        pass