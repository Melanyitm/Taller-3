from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.actividad2 import ROLES


class UsuarioBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=255)
    correo: str = Field(min_length=3, max_length=255)
    rol: str
    activo: bool = True

    @field_validator("rol")
    @classmethod
    def rol_valido(cls, v: str) -> str:
        if v not in ROLES:
            raise ValueError(f"rol debe ser uno de: {', '.join(ROLES)}")
        return v


class UsuarioCreate(UsuarioBase):
    password: str = Field(min_length=6, max_length=128)


class UsuarioRead(UsuarioBase):
    id_usuario: int

    model_config = ConfigDict(from_attributes=True)
