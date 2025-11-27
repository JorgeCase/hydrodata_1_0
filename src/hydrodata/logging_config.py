import logging
from logging import Logger


def setup_logging(verbose: bool = False) -> Logger:
    """
    Configura o logging da aplicação.

    - Se verbose = True: Define o nível de logging para DEBUG.
    - Se verbose = False: Define o nível de logging para INFO.

    Retorna o logger raiz para uso opcional.
    """

    level = logging.DEBUG if verbose else logging.INFO

    # Evita reconfirgurar se já houver handlers
    if logging.getLogger().handlers:
        logging.getLogger().setLevel(level)
        return logging.getLogger()

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger = logging.getLogger("hydrodata")
    logger.debug("Logging configurado (verbose=%s).", verbose)
    return logger
