from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas.usuario import UsuarioCreate, UsuarioRead

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)):
    existe = db.scalars(select(models.Usuario).where(models.Usuario.correo == payload.correo)).first()
    if existe:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo ya está registrado")
    usuario = models.Usuario(
        nombre=payload.nombre,
        correo=payload.correo,
        password_hash=pwd_context.hash(payload.password),
        rol=payload.rol,
        activo=payload.activo,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
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
