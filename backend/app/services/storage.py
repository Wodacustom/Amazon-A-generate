"""RustFS/S3 对象存储封装。"""

import asyncio
from dataclasses import dataclass
from uuid import uuid4

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.core.config import settings


@dataclass(frozen=True)
class StoredObject:
    """上传完成后返回给业务层的对象元数据。"""

    bucket: str
    object_key: str
    url: str
    size_bytes: int
    content_type: str | None


class ObjectStorage:
    """使用 boto3 访问 S3 兼容对象存储。"""

    def __init__(self) -> None:
        """创建 S3 客户端，RustFS 使用 path-style 地址。"""
        self._client = self._create_client(settings.s3_endpoint_url)
        self._public_client = self._create_client(settings.s3_public_base_url or settings.s3_endpoint_url)

    def _create_client(self, endpoint_url: str):
        """创建指定 endpoint 的 S3 客户端。"""
        return boto3.client(
            "s3",
            endpoint_url=endpoint_url,
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
        """确保默认 bucket 存在。"""
        await asyncio.to_thread(self._ensure_bucket_sync)

    async def put_bytes(
        self, data: bytes, filename: str | None, content_type: str | None, *, prefix: str = "uploads"
    ) -> StoredObject:
        """上传字节内容到对象存储。"""
        await self.ensure_bucket()
        suffix = ""
        if filename and "." in filename:
            suffix = "." + filename.rsplit(".", 1)[1].lower()
        # 使用 UUID 作为对象名，避免用户文件名导致冲突或路径穿越问题。
        object_key = f"{prefix.strip('/')}/{uuid4()}{suffix}"
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

    async def presign_get_url(self, object_key: str, *, expires_in: int = 7200) -> str:
        """生成对象临时访问链接。"""
        return await asyncio.to_thread(
            self._public_client.generate_presigned_url,
            "get_object",
            Params={"Bucket": settings.s3_bucket, "Key": object_key},
            ExpiresIn=expires_in,
        )

    async def get_bytes(self, object_key: str) -> tuple[bytes, str | None]:
        """从对象存储读取文件内容。"""
        response = await asyncio.to_thread(self._client.get_object, Bucket=settings.s3_bucket, Key=object_key)
        body = await asyncio.to_thread(response["Body"].read)
        return body, response.get("ContentType")

    def _ensure_bucket_sync(self) -> None:
        """同步 boto3 调用：不存在时创建 bucket。"""
        try:
            self._client.head_bucket(Bucket=settings.s3_bucket)
        except ClientError:
            self._client.create_bucket(Bucket=settings.s3_bucket)


def get_storage() -> ObjectStorage:
    """返回对象存储客户端实例。"""
    return ObjectStorage()
