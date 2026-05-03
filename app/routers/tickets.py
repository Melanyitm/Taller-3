from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import AuthContext, get_auth_context
from app import models
from app.domain.ticket_rules import (
    ASSIGNABLE_ROLES,
    puede_atender_ticket,
    puede_finalizar_ticket,
    puede_gestionar_como_responsable_del_ticket,
    puede_ver_ticket,
    scope_para_transicion,
    es_admin,
)
from app.schemas.ticket import TicketCreate, TicketEstadoPatch, TicketRead

router = APIRouter()


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


@router.post("/", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def crear_ticket(
    payload: TicketCreate,
    auth: Annotated[AuthContext, Security(get_auth_context, scopes=["tickets:crear"])],
    db: Session = Depends(get_db),
):
    if not es_admin(auth.usuario) and payload.id_solicitante != auth.usuario.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puede crear tickets donde usted es el solicitante",
        )
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
def listar_tickets(
    auth: Annotated[AuthContext, Security(get_auth_context, scopes=["tickets:ver_propios"])],
    db: Session = Depends(get_db),
):
    q = select(models.Ticket)
    if "tickets:ver_todos" not in auth.scopes:
        uid = auth.usuario.id_usuario
        q = q.where(
            or_(
                models.Ticket.id_solicitante == uid,
                models.Ticket.id_responsable == uid,
                models.Ticket.id_asignado == uid,
            )
        )
    q = q.order_by(models.Ticket.id_ticket)
    return list(db.scalars(q).all())


@router.get("/{id_ticket}", response_model=TicketRead)
def obtener_ticket(
    id_ticket: int,
    auth: Annotated[AuthContext, Security(get_auth_context, scopes=["tickets:ver_propios"])],
    db: Session = Depends(get_db),
):
    ticket = db.get(models.Ticket, id_ticket)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado")
    if not puede_ver_ticket(auth.usuario, auth.scopes, ticket):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No está autorizado para ver este ticket",
        )
    return ticket


@router.patch("/{id_ticket}/estado", response_model=TicketRead)
def actualizar_estado_ticket(
    id_ticket: int,
    payload: TicketEstadoPatch,
    auth: Annotated[AuthContext, Security(get_auth_context, scopes=[])],
    db: Session = Depends(get_db),
):
    ticket = db.get(models.Ticket, id_ticket)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado")
    if not puede_ver_ticket(auth.usuario, auth.scopes, ticket):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No está autorizado para modificar este ticket",
        )

    actual = ticket.estado
    nuevo = payload.estado
    if nuevo == actual:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El estado solicitado es igual al actual; no hay transición",
        )

    req_scope = scope_para_transicion(actual, nuevo)
    if req_scope is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Transición no permitida: {actual} → {nuevo}",
        )
    if req_scope not in auth.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Se requiere el scope «{req_scope}» para esta transición",
        )

    if actual == "solicitado" and nuevo == "recibido":
        if auth.usuario.rol not in ("responsable_tecnico", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el responsable técnico o administrador pueden recibir el ticket",
            )
        ticket.id_responsable = auth.usuario.id_usuario

    elif actual == "recibido" and nuevo == "asignado":
        if not puede_gestionar_como_responsable_del_ticket(auth.usuario, ticket):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el responsable del ticket o el administrador pueden asignarlo",
            )
        if payload.id_asignado is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Debe enviar id_asignado al pasar de recibido a asignado",
            )
        asignado = db.get(models.Usuario, payload.id_asignado)
        if not asignado or asignado.rol not in ASSIGNABLE_ROLES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="id_asignado debe existir y ser auxiliar o técnico especializado",
            )
        ticket.id_asignado = payload.id_asignado

    elif (actual, nuevo) in (("asignado", "en_proceso"), ("en_proceso", "en_revision")):
        if not puede_atender_ticket(auth.usuario, ticket):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el técnico asignado o el administrador pueden atender este ticket",
            )

    elif actual == "en_revision" and nuevo == "terminado":
        if not puede_finalizar_ticket(auth.usuario, ticket):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el responsable del ticket o el administrador pueden finalizarlo",
            )

    ticket.estado = nuevo
    if payload.observacion_responsable is not None:
        ticket.observacion_responsable = payload.observacion_responsable
    if payload.observacion_tecnico is not None:
        ticket.observacion_tecnico = payload.observacion_tecnico
    ticket.fecha_actualizacion = _ahora()
    if nuevo == "terminado":
        ticket.fecha_finalizacion = _ahora()

    db.commit()
    db.refresh(ticket)
    return ticket
