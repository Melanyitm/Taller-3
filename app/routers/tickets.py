from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas.ticket import TicketCreate, TicketEstadoPatch, TicketRead

router = APIRouter()


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


@router.post("/", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def crear_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    if not db.get(models.Usuario, payload.id_solicitante):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="id_solicitante no existe")
    if not db.get(models.Laboratorio, payload.id_laboratorio):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="id_laboratorio no existe")
    if not db.get(models.Servicio, payload.id_servicio):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="id_servicio no existe")

    ahora = _ahora()
    ticket = models.Ticket(
        id_solicitante=payload.id_solicitante,
        id_laboratorio=payload.id_laboratorio,
        id_servicio=payload.id_servicio,
        titulo=payload.titulo,
        descripcion=payload.descripcion,
        prioridad=payload.prioridad,
        estado="solicitado",
        fecha_actualizacion=ahora,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/", response_model=list[TicketRead])
def listar_tickets(db: Session = Depends(get_db)):
    return list(db.scalars(select(models.Ticket).order_by(models.Ticket.id_ticket)).all())


@router.get("/{id_ticket}", response_model=TicketRead)
def obtener_ticket(id_ticket: int, db: Session = Depends(get_db)):
    ticket = db.get(models.Ticket, id_ticket)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado")
    return ticket


@router.patch("/{id_ticket}/estado", response_model=TicketRead)
def actualizar_estado_ticket(
    id_ticket: int,
    payload: TicketEstadoPatch,
    db: Session = Depends(get_db),
):
    ticket = db.get(models.Ticket, id_ticket)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado")

    ticket.estado = payload.estado
    if payload.observacion_responsable is not None:
        ticket.observacion_responsable = payload.observacion_responsable
    if payload.observacion_tecnico is not None:
        ticket.observacion_tecnico = payload.observacion_tecnico
    ticket.fecha_actualizacion = _ahora()
    if payload.estado == "terminado":
        ticket.fecha_finalizacion = _ahora()

    db.commit()
    db.refresh(ticket)
    return ticket
