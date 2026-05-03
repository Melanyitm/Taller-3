from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.domain.actividad2 import ROLE_SCOPES
from app.core.security import create_access_token, verify_password
from app.schemas.token import Token

router = APIRouter()


@router.post("/token", response_model=Token)
def login_access_token(
    db: Annotated[Session, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """OAuth2 compatible: enviar `username` = correo y `password` (form-data o x-www-form-urlencoded)."""
    usuario = db.scalars(select(models.Usuario).where(models.Usuario.correo == form_data.username)).first()
    if not usuario or not verify_password(form_data.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not usuario.activo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo")

    scopes = sorted(ROLE_SCOPES.get(usuario.rol, frozenset()))
    access_token = create_access_token(
        sub=usuario.correo,
        id_usuario=usuario.id_usuario,
        rol=usuario.rol,
        scopes=scopes,
    )
    return Token(access_token=access_token)
