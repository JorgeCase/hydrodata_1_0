from __future__ import annotations

from typing import Optional
from pathlib import Path

import typer

from hydrodata import __version__
from hydrodata.core.models import Station
from hydrodata.logging_config import setup_logging
from hydrodata.infrastructure.http_client import (
    HttpClient,
    RecordingHttpClient,
    RequestsHttpClient,
)
from hydrodata.infrastructure.spatial import (
    load_aoi,
    filter_stations_in_aoi
)
from hydrodata.providers.ana_client import ANAClient

app = typer.Typer(help="hydrodata - Ferramenta para dados hidrológicos (ANA/INMET).")


def _build_http_client(mode: str) -> HttpClient:
    """
    Cria o cliente HTTP de acordo com o modo escolhido.

    mode:
        - "real": RequestsHttpClient simples
        - "record": RecordingHttpClient + RequestsHttpClient
    """
    if mode == "record":
        real = RequestsHttpClient()
        return RecordingHttpClient(inner=real)

    # default: real
    return RequestsHttpClient()


@app.callback()
def main(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Ativa saída detalhada (modo verboso).",
    ),
):
    """
    Ponto de entrada principal da CLI.
    Aqui configuramos o logging antes de qualquer comando ser executado.
    """
    setup_logging(verbose=verbose)


@app.command()
def version():
    """Mostra a versão atual do hydrodata."""
    typer.echo(f"hydrodata version: {__version__}")


@app.command()
def hello(
    name: Optional[str] = typer.Argument(
        None,
        help="Nome da pessoa para cumprimentar.",
    ),
):
    """
    Comando de teste apenas para verificar se a CLI está funcionando.
    """
    if not name:
        name = "Mundo"
    typer.echo(f"Olá, {name}! O hydrodata está pronto para trabalhar.")


@app.command("ana-download")
def ana_download(
    station: list[int] = typer.Option(
        ...,
        "--station",
        "-s",
        help="Código(s) de estação(ões) da ANA para download."
    ),
    mode: str = typer.Option(
        "real",
        "--mode",
        "-m",
        help="Modo de operação HTTP: 'real' ou 'record'.",
        case_sensitive=False,
    ),
):
    """
    Faz o download de dados brutos da ANA para uma ou mais estações.

    ATENÇÃO:
        No momento, este comando é apenas um ESQUELETO e usa uma URL
        fictícia na ANA, Será ajustado nos próximos passos.
    """
    http_client = _build_http_client(mode.lower())
    ana_client = ANAClient(http_client=http_client)

    typer.echo(f"Iniciando download para estações: {station} (modo={mode})")

    try:
        paths = ana_client.download_station_files(station)
    except Exception as exc:
        typer.secho(f"Erro ao tentar baixar dados da ANA: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    for p in paths:
        typer.secho(f"Arquico salvo em: {p}", fg=typer.colors.GREEN)


@app.command("spatial-test")
def spatial_test(
    shapefile: Path = typer.Option(
        ...,
        "--shapefile",
        "-f",
        exists=True,
        readable=True,
        resolve_path=True,
        help="Caminho para o shapefile da área de interesse (AOI).",
    ),
):
    """
    Testa o carregamento de um shapefile e o filtro espacial de estações.

    Este comando usa estações MOCK (valores de exemplo) apenas para
    verificar se o pipeline geoespacial está funcionando.
    """
    typer.echo(f"Carregando AOI de: {shapefile}")
    aoi_geom = load_aoi(shapefile)

    # TODO: no futuro, vamos obter as estações reais via ANA/INMET.
    # Por enquanto, estações de exemplo:
    stations = [
        Station(
            code=1,
            name="Estação Exemplo 1",
            station_type="pluviometrica",
            latitude=-6.90,
            longitude=-36.20,
            altitude=500.0,
        ),
        Station(
            code=2,
            name="Estação Exemplo 2",
            station_type="fluviometrica",
            latitude=-6.95,
            longitude=-36.25,
            altitude=480.0,
        ),
        Station(
            code=3,
            name="Estação Fora",
            station_type="pluviometrica",
            latitude=0.0,
            longitude=0.0,
            altitude=None,
        ),
    ]

    typer.echo(f"Total de estações mock: {len(stations)}")

    stations_in_aoi = filter_stations_in_aoi(stations, aoi_geom)

    typer.echo(f"Estações dentro da AOI: {len(stations_in_aoi)}")
    for st in stations_in_aoi:
        typer.echo(
            f"- {st.code} | {st.name} | {st.station_type} "
            f"| ({st.latitude}, {st.longitude}) alt={st.altitude}"
        )
