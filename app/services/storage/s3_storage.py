import boto3
import os
from uuid import uuid4

from .storage_interface import StorageInterface


class S3Storage(StorageInterface):

    def __init__(self):
        self.bucket = os.getenv("S3_BUCKET_NAME")
        self.client = boto3.client("s3")

    def upload(self, file):

        extension = os.path.splitext(file.filename)[1]

        key = f"uploads/{uuid4()}{extension}"

        self.client.upload_fileobj(
            file.file,
            self.bucket,
            key
        )

        return key

    def download(self, key):
        pass

    def delete(self, key):
        pass