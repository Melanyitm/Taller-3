from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.database import Base

_schema = settings.db_schema


def _fk(table: str, column: str) -> ForeignKey:
    return ForeignKey(f"{_schema}.{table}.{column}")


class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": _schema}

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    correo: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(64), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Laboratorio(Base):
    __tablename__ = "laboratorios"
    __table_args__ = {"schema": _schema}

    id_laboratorio: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    ubicacion: Mapped[str] = mapped_column(String(255), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Servicio(Base):
    __tablename__ = "servicios"
    __table_args__ = {"schema": _schema}

    id_servicio: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = {"schema": _schema}

    id_ticket: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_solicitante: Mapped[int] = mapped_column(_fk("usuarios", "id_usuario"), nullable=False)
    id_laboratorio: Mapped[int] = mapped_column(_fk("laboratorios", "id_laboratorio"), nullable=False)
    id_servicio: Mapped[int] = mapped_column(_fk("servicios", "id_servicio"), nullable=False)
    id_responsable: Mapped[int | None] = mapped_column(
        _fk("usuarios", "id_usuario"),
        nullable=True,
    )
    id_asignado: Mapped[int | None] = mapped_column(
        _fk("usuarios", "id_usuario"),
        nullable=True,
    )
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[str] = mapped_column(String(64), nullable=False, default="solicitado")
    prioridad: Mapped[str] = mapped_column(String(32), nullable=False, default="media")
    observacion_responsable: Mapped[str | None] = mapped_column(Text, nullable=True)
    observacion_tecnico: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    fecha_finalizacion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    solicitante: Mapped[Usuario] = relationship("Usuario", foreign_keys=[id_solicitante])
    responsable: Mapped[Usuario | None] = relationship("Usuario", foreign_keys=[id_responsable])
    asignado_a: Mapped[Usuario | None] = relationship("Usuario", foreign_keys=[id_asignado])
    laboratorio: Mapped[Laboratorio] = relationship("Laboratorio", foreign_keys=[id_laboratorio])
    servicio: Mapped[Servicio] = relationship("Servicio", foreign_keys=[id_servicio])
