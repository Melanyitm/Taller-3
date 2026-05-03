from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas.servicio import ServicioCreate, ServicioRead

router = APIRouter()


@router.post("/", response_model=ServicioRead, status_code=status.HTTP_201_CREATED)
def crear_servicio(payload: ServicioCreate, db: Session = Depends(get_db)):
    servicio = models.Servicio(
        nombre=payload.nombre,
        descripcion=payload.descripcion,
        activo=payload.activo,
    )
    db.add(servicio)
    db.commit()
    db.refresh(servicio)
    return servicio


@router.get("/", response_model=list[ServicioRead])
def listar_servicios(db: Session = Depends(get_db)):
    return list(db.scalars(select(models.Servicio).order_by(models.Servicio.id_servicio)).all())


@router.get("/{id_servicio}", response_model=ServicioRead)
def obtener_servicio(id_servicio: int, db: Session = Depends(get_db)):
    servicio = db.get(models.Servicio, id_servicio)
    if not servicio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")
    return servicio
