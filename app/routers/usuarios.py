from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app import models
from app.core.security import get_password_hash
from app.schemas.usuario import UsuarioCreate, UsuarioRead

router = APIRouter()


@router.post("/", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)):
    existe = db.scalars(select(models.Usuario).where(models.Usuario.correo == payload.correo)).first()
    if existe:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo ya está registrado")
    usuario = models.Usuario(
        nombre=payload.nombre,
        correo=payload.correo,
        password_hash=get_password_hash(payload.password),
        rol=payload.rol,
        activo=payload.activo,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.get("/me", response_model=UsuarioRead)
def leer_usuario_actual(usuario: Annotated[models.Usuario, Depends(get_current_user)]):
    """Requiere encabezado `Authorization: Bearer <token>`. Útil para probar JWT en Swagger."""
    return usuario


@router.get("/", response_model=list[UsuarioRead])
def listar_usuarios(db: Session = Depends(get_db)):
    return list(db.scalars(select(models.Usuario).order_by(models.Usuario.id_usuario)).all())


@router.get("/{id_usuario}", response_model=UsuarioRead)
def obtener_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usuario = db.get(models.Usuario, id_usuario)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return usuario
