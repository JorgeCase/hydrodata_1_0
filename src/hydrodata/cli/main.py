from typing import Optional

import typer

from hydrodata import __version__

app = typer.Typer(help="hydrodata - Ferramentas para dados hidrológicos (ANA/INMET).")


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

    Por enquanto, esta função apenas prepara o 'contexto' da aplicação.
    No futuro, podemos usar 'verbose' para configurar logging, etc.
    """
    if verbose:
        typer.echo("Modo verboso ativado.")


@app.command()
def version():
    """Mostra a versão atual do hydrodata."""
    typer.echo(f"hydrodata versão {__version__}")


@app.command()
def hello(
    name: Optional[str] = typer.Argument(
        None, help="Nome da pessoa para cumprimentar."
    ),
):
    """
    Comando de teste apenas para verificar se a CLI está funcionando.
    """
    if not name:
        name = "mundo"
    typer.echo(f"Olá, {name}! O hydrodata está pronto para trabalhar.")


if __name__ == "__main__":
    app()
