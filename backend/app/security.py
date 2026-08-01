from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_setting(name: str, default: Any):
    return getattr(settings, name, default)


SECRET_KEY = get_setting("SECRET_KEY", "digidarshan-dev-secret-key")
ALGORITHM = get_setting("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = get_setting("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: int | str, extra_claims: dict | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(subject),
        "exp": expire,
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)