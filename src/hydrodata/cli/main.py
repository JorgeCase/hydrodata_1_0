from __future__ import annotations

from typing import Optional

import typer

from hydrodata import __version__
from hydrodata.logging_config import setup_logging
from hydrodata.infrastructure.http_client import (
    HttpClient,
    RecordingHttpClient,
    RequestsHttpClient,
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
