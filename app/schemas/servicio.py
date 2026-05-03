from pydantic import BaseModel, ConfigDict, Field


class ServicioBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=255)
    descripcion: str = Field(min_length=1)
    activo: bool = True


class ServicioCreate(ServicioBase):
    pass


class ServicioRead(ServicioBase):
    id_servicio: int

    model_config = ConfigDict(from_attributes=True)
