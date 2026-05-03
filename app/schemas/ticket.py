from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.actividad2 import ESTADOS_TICKET, PRIORIDADES


class TicketBase(BaseModel):
    titulo: str = Field(min_length=1, max_length=255)
    descripcion: str = Field(min_length=1)
    prioridad: str = "media"

    @field_validator("prioridad")
    @classmethod
    def prioridad_valida(cls, v: str) -> str:
        if v not in PRIORIDADES:
            raise ValueError(f"prioridad debe ser una de: {', '.join(PRIORIDADES)}")
        return v


class TicketCreate(TicketBase):
    id_solicitante: int
    id_laboratorio: int
    id_servicio: int


class TicketRead(TicketBase):
    id_ticket: int
    id_solicitante: int
    id_laboratorio: int
    id_servicio: int
    id_responsable: int | None
    id_asignado: int | None
    estado: str
    observacion_responsable: str | None
    observacion_tecnico: str | None
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    fecha_finalizacion: datetime | None

    model_config = ConfigDict(from_attributes=True)


class TicketEstadoPatch(BaseModel):
    estado: str
    observacion_responsable: str | None = None
    observacion_tecnico: str | None = None
    id_asignado: int | None = Field(
        default=None,
        description="Obligatorio al pasar de recibido a asignado.",
    )

    @field_validator("estado")
    @classmethod
    def estado_valido(cls, v: str) -> str:
        if v not in ESTADOS_TICKET:
            raise ValueError(f"estado debe ser uno de: {', '.join(ESTADOS_TICKET)}")
        return v
