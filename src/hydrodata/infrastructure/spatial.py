from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, List

import geopandas as gpd
from shapely.geometry import Point
from shapely.geometry.base import BaseGeometry

from hydrodata.core.models import Station

logger = logging.getLogger("hydrodata.spatial")


def load_aoi(shapefile_path: Path | str) -> BaseGeometry:
    """
    Carrega um shapefile da área de interesse (AOI) e
    retorna uma geometria unica.

    - Reprojeta para EPSG:4326 (lat/lon) para ficar coerente com as estações.
    - Faz um 'dissolve' geométrico usando unary_union (ou union_all
    em versões recentes).

    Retorna:
        BaseGeometry: (Polygon ou MultiPolygon)
    """
    path = Path(shapefile_path)
    if not path.exists():
        msg = f"Shapefile não encontrado: {shapefile_path}"
        logger.error(msg)
        raise FileNotFoundError(msg)

    logger.info("Carregando AOI a partir de %s", path)
    gdf = gpd.read_file(path)

    if gdf.empty:
        msg = f"Shapefile vazio: {path}"
        logger.error(msg)
        raise ValueError(msg)

    # Garante um CRS conhecido; se não tiver, assume EPSG:4326
    if gdf.crs is None:
        logger.warning(
            "Shapefile %s sem CRS definido. Assumindo EPSG:4326. "
            "Veridique se isso é correto.",
            path,
        )
        gdf = gdf.set_crs(epsg=4326)
    else:
        # Reprojetar para EPSG:4326, pois as estações usam lat/lon
        if gdf.crs.to_epsg() != 4326:
            logger.info(
                "Reprojetando AOI de %s para EPSG:4326", gdf.crs
            )
            gdf = gdf.to_crs(epsg=4326)

    # Unificar geometria (se tiver múltiplos polígonos)
    geometry = gdf.unary_union
    logger.info("AOI carregada com área aproximada: %s", geometry.area)

    return geometry


def filter_stations_in_aoi(
    stations: Iterable[Station],
    aoi_geometry: BaseGeometry,
) -> List[Station]:
    """
    Filtra estações que estão dentro da área de interesse (AOI).

    Critério:
        - Usa o método 'within' (ponto dentro do polígono).

    Retorna:
        Lista de Station dentro da AOI.
    """
    stations_list = list(stations)  # garante que podemos iterar e contar
    result: list[Station] = []

    for st in stations_list:
        pt = Point(st.longitude, st.latitude)
        if pt.within(aoi_geometry):
            result.append(st)

    logger.info(
        "Filtradas %d estações dentro da AOI (de um total de %d).",
        len(result),
        len(stations_list),
    )
    return result
