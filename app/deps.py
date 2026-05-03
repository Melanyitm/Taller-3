from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import SecurityScopes
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import oauth2_scheme
from app.database import get_db
from app import models

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No se pudieron validar las credenciales",
    headers={"WWW-Authenticate": "Bearer"},
)


@dataclass(frozen=True)
class AuthContext:
    usuario: models.Usuario
    scopes: frozenset[str]


def get_auth_context(
    security_scopes: SecurityScopes,
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> AuthContext:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        sub = payload.get("sub")
        uid = payload.get("id_usuario")
        raw_scopes = payload.get("scopes") or []
        if not isinstance(sub, str) or uid is None:
            raise credentials_exception
        try:
            uid_int = int(uid)
        except (TypeError, ValueError):
            raise credentials_exception
        if not isinstance(raw_scopes, list):
            raise credentials_exception
        token_scopes = frozenset(str(s) for s in raw_scopes)
    except JWTError:
        raise credentials_exception

    authenticate_value = "Bearer"
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'

    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permisos insuficientes: se requiere el scope «{scope}»",
                headers={"WWW-Authenticate": authenticate_value},
            )

    usuario = db.get(models.Usuario, uid_int)
    if not usuario or usuario.correo != sub or not usuario.activo:
        raise credentials_exception

    return AuthContext(usuario=usuario, scopes=token_scopes)


def get_current_user(
    auth: Annotated[AuthContext, Security(get_auth_context, scopes=[])],
) -> models.Usuario:
    return auth.usuario
