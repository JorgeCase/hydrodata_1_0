from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class Station(BaseModel):
    code: int = Field(
        ..., description="Código oficial da estação (ANA, INMET, etc.).")
    name: str = Field(..., description="Nome da estação.")
    station_type: str = Field(
        ...,
        description="Tipo da estação (ex.: 'pluviometrica', 'fluviometrica').",
    )
    latitude: float = Field(
        ..., description="Latitude em graus decimais (EPSG:4326).")
    longitude: float = Field(
        ...,
        description="Longitude em graus decimais (EPSG:4326).",
    )
    altitude: Optional[float] = Field(
        default=None,
        description="Altitude da estação em metros (opcional).",
    )

    class Config:
        frozen = True  # imutável (bom para evitar bugs)
