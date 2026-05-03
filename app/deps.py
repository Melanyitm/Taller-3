from typing import Annotated

from fastapi import Depends, HTTPException, status
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


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> models.Usuario:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        sub = payload.get("sub")
        uid = payload.get("id_usuario")
        if not isinstance(sub, str) or uid is None:
            raise credentials_exception
        try:
            uid_int = int(uid)
        except (TypeError, ValueError):
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    usuario = db.get(models.Usuario, uid_int)
    if not usuario or usuario.correo != sub or not usuario.activo:
        raise credentials_exception
    return usuario
