import os
import re
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

_SCHEMA_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


@dataclass(frozen=True)
class Settings:
    database_url: str
    db_schema: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Falta la variable de entorno obligatoria: {name}")
    return value


def _schema() -> str:
    raw = os.getenv("DB_SCHEMA", "").strip()
    if not raw:
        raise RuntimeError(
            "Define DB_SCHEMA en .env con el nombre del schema asignado por el docente "
            "(no uses el schema public si la guía indica lo contrario)."
        )
    if not _SCHEMA_RE.match(raw):
        raise RuntimeError("DB_SCHEMA debe ser un identificador SQL válido (letras, números, _).")
    return raw


def get_settings() -> Settings:
    return Settings(
        database_url=_require_env("DATABASE_URL"),
        db_schema=_schema(),
        secret_key=_require_env("SECRET_KEY"),
        algorithm=os.getenv("ALGORITHM", "HS256"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
    )


settings = get_settings()
