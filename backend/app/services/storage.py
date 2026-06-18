import asyncio
from dataclasses import dataclass
from uuid import uuid4

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.core.config import settings


@dataclass(frozen=True)
class StoredObject:
    bucket: str
    object_key: str
    url: str
    size_bytes: int
    content_type: str | None


class ObjectStorage:
    def __init__(self) -> None:
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key.get_secret_value(),
            region_name=settings.s3_region,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
                connect_timeout=1,
                read_timeout=1,
                retries={"max_attempts": 1},
            ),
        )

    async def ensure_bucket(self) -> None:
        await asyncio.to_thread(self._ensure_bucket_sync)

    async def put_bytes(self, data: bytes, filename: str | None, content_type: str | None) -> StoredObject:
        await self.ensure_bucket()
        suffix = ""
        if filename and "." in filename:
            suffix = "." + filename.rsplit(".", 1)[1].lower()
        object_key = f"uploads/{uuid4()}{suffix}"
        await asyncio.to_thread(
            self._client.put_object,
            Bucket=settings.s3_bucket,
            Key=object_key,
            Body=data,
            ContentType=content_type or "application/octet-stream",
        )
        return StoredObject(
            bucket=settings.s3_bucket,
            object_key=object_key,
            url=f"/api/files/{object_key}/content",
            size_bytes=len(data),
            content_type=content_type,
        )

    async def get_bytes(self, object_key: str) -> tuple[bytes, str | None]:
        response = await asyncio.to_thread(self._client.get_object, Bucket=settings.s3_bucket, Key=object_key)
        body = await asyncio.to_thread(response["Body"].read)
        return body, response.get("ContentType")

    def _ensure_bucket_sync(self) -> None:
        try:
            self._client.head_bucket(Bucket=settings.s3_bucket)
        except ClientError:
            self._client.create_bucket(Bucket=settings.s3_bucket)


def get_storage() -> ObjectStorage:
    return ObjectStorage()
