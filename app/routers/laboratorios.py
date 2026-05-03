from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas.laboratorio import LaboratorioCreate, LaboratorioRead

router = APIRouter()


@router.post("/", response_model=LaboratorioRead, status_code=status.HTTP_201_CREATED)
def crear_laboratorio(payload: LaboratorioCreate, db: Session = Depends(get_db)):
    lab = models.Laboratorio(
        nombre=payload.nombre,
        ubicacion=payload.ubicacion,
        activo=payload.activo,
    )
    db.add(lab)
    db.commit()
    db.refresh(lab)
    return lab


@router.get("/", response_model=list[LaboratorioRead])
def listar_laboratorios(db: Session = Depends(get_db)):
    return list(db.scalars(select(models.Laboratorio).order_by(models.Laboratorio.id_laboratorio)).all())


@router.get("/{id_laboratorio}", response_model=LaboratorioRead)
def obtener_laboratorio(id_laboratorio: int, db: Session = Depends(get_db)):
    lab = db.get(models.Laboratorio, id_laboratorio)
    if not lab:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Laboratorio no encontrado")
    return lab
