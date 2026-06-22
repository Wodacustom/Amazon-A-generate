"""认证 token、密码哈希和模型密钥保护。"""

import base64
import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.config import settings


class SecurityConfigurationError(RuntimeError):
    """安全配置缺失。"""


def hash_password(password: str, *, salt: str | None = None) -> str:
    """使用 PBKDF2 生成密码哈希。

    返回格式包含算法、迭代次数、salt 和 digest，便于后续升级算法。
    """
    raw_salt = base64.urlsafe_b64decode(salt.encode("ascii")) if salt else os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), raw_salt, 120_000)
    return "pbkdf2_sha256$120000${}${}".format(
        base64.urlsafe_b64encode(raw_salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, stored: str) -> bool:
    """校验密码。"""
    try:
        algorithm, iterations, salt, digest = stored.split("$", 3)
    except ValueError:
        return hmac.compare_digest(password, stored)
    if algorithm != "pbkdf2_sha256":
        return False
    raw_salt = base64.urlsafe_b64decode(salt.encode("ascii"))
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), raw_salt, int(iterations))
    return hmac.compare_digest(base64.urlsafe_b64encode(candidate).decode("ascii"), digest)


def create_access_token(subject: str, role: str) -> str:
    """创建简单 HS256 JWT。

    项目当前不额外引入 PyJWT；这里用标准库实现最小 Bearer token。
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expire_minutes)).timestamp()),
    }
    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = ".".join(
        [
            _b64url_json(header),
            _b64url_json(payload),
        ]
    )
    signature = _sign(signing_input)
    return f"{signing_input}.{signature}"


def decode_access_token(token: str) -> dict[str, Any]:
    """解析并验证 JWT。"""
    try:
        header_part, payload_part, signature = token.split(".", 2)
    except ValueError as exc:
        raise ValueError("Invalid token.") from exc
    signing_input = f"{header_part}.{payload_part}"
    if not hmac.compare_digest(_sign(signing_input), signature):
        raise ValueError("Invalid token signature.")
    payload = json.loads(_b64url_decode(payload_part).decode("utf-8"))
    if int(payload.get("exp", 0)) < int(time.time()):
        raise ValueError("Token expired.")
    return payload


def encrypt_secret(value: str) -> str:
    """加密模型密钥。

    加密结果包含 nonce、HMAC 和密文；接口层永远不返回解密后的完整 API key。
    """
    key = _model_secret_key()
    nonce = os.urandom(16)
    stream = _key_stream(key, nonce, len(value.encode("utf-8")))
    encrypted = bytes(a ^ b for a, b in zip(value.encode("utf-8"), stream, strict=True))
    mac = hmac.new(key, nonce + encrypted, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(nonce + mac + encrypted).decode("ascii")


def decrypt_secret(value: str | None) -> str | None:
    """解密模型密钥。"""
    if not value:
        return None
    key = _model_secret_key()
    raw = base64.urlsafe_b64decode(value.encode("ascii"))
    nonce, mac, encrypted = raw[:16], raw[16:48], raw[48:]
    expected = hmac.new(key, nonce + encrypted, hashlib.sha256).digest()
    if not hmac.compare_digest(mac, expected):
        raise ValueError("Encrypted secret verification failed.")
    stream = _key_stream(key, nonce, len(encrypted))
    return bytes(a ^ b for a, b in zip(encrypted, stream, strict=True)).decode("utf-8")


def mask_secret(value: str | None) -> str | None:
    """隐藏密钥明文。"""
    if not value:
        return None
    if len(value) <= 8:
        return "****"
    return f"{value[:4]}****{value[-4:]}"


def _model_secret_key() -> bytes:
    """从 MODEL_CONFIG_SECRET_KEY 派生固定长度密钥。"""
    if settings.model_config_secret_key is None or not settings.model_config_secret_key.get_secret_value():
        raise SecurityConfigurationError("MODEL_CONFIG_SECRET_KEY is required to store model API keys.")
    return hashlib.sha256(settings.model_config_secret_key.get_secret_value().encode("utf-8")).digest()


def _key_stream(key: bytes, nonce: bytes, length: int) -> bytes:
    """用 HMAC 派生伪随机字节流，与明文异或得到密文。"""
    chunks = []
    counter = 0
    while sum(len(chunk) for chunk in chunks) < length:
        chunks.append(hmac.new(key, nonce + counter.to_bytes(4, "big"), hashlib.sha256).digest())
        counter += 1
    return b"".join(chunks)[:length]


def _b64url_json(payload: dict[str, Any]) -> str:
    data = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def _sign(signing_input: str) -> str:
    secret = settings.jwt_secret_key.get_secret_value().encode("utf-8")
    return base64.urlsafe_b64encode(hmac.new(secret, signing_input.encode("ascii"), hashlib.sha256).digest()).rstrip(
        b"="
    ).decode("ascii")
