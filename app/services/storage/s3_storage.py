import os
from uuid import uuid4

import boto3
from botocore.config import Config

from .storage_interface import StorageInterface


class S3Storage(StorageInterface):

    def __init__(self):
        self.bucket = os.getenv("S3_BUCKET_NAME")

        self.client = boto3.client(
            "s3",
            region_name=os.getenv("AWS_REGION"),
            config=Config(signature_version="s3v4"),
        )

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

        return self.client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket,
                "Key": key,
            },
            ExpiresIn=300,
        )

    def delete(self, key):
        self.client.delete_object(
            Bucket=self.bucket,
            Key=key,
        )