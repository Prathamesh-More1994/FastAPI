from datetime import timedelta, datetime, timezone

from jose import jwt
from passlib.context import CryptContext

from .config import SECRET_KEY, ALGORITHM


bcrypt_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)


def create_access_token(
    username: str,
    user_id: int,
    role: str,
    expires_delta: timedelta
) -> str:
    encode = {
        "sub": username,
        "id": user_id,
        "role": role
    }

    expires = datetime.now(timezone.utc) + expires_delta
    encode["exp"] = expires

    return jwt.encode(
        encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )