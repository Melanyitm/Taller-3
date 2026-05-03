from datetime import datetime, timedelta, timezone

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(*, sub: str, id_usuario: int, rol: str, scopes: list[str]) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {
        "sub": sub,
        "id_usuario": id_usuario,
        "rol": rol,
        "scopes": scopes,
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
