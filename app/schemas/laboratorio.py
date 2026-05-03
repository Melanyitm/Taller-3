from pydantic import BaseModel, ConfigDict, Field


class LaboratorioBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=255)
    ubicacion: str = Field(min_length=1, max_length=255)
    activo: bool = True


class LaboratorioCreate(LaboratorioBase):
    pass


class LaboratorioRead(LaboratorioBase):
    id_laboratorio: int

    model_config = ConfigDict(from_attributes=True)
