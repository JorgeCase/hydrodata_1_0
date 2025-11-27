from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional
from zipfile import ZipFile

logger = logging.getLogger("hydrodata.storage")


def ensure_dir(path: Path | str) -> Path:
    """
    Garante que o diretório existe e retorna o Path correspondente.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_bytes_to_file(
    content: bytes,
    target_dir: Path | str,
    filename: str,
    overwrite: bool = False,
) -> Path:
    """
    Salva bytes em arquivo dentro de um diretório alvo, retornando o caminho.
    """
    directory = ensure_dir(target_dir)
    path = directory / filename

    if path.exists() and not overwrite:
        logger.info("Arquivo já existente, não será sobrescrito: %s", path)
        return path

    path.write_bytes(content)
    logger.info("Arquivo salvo em: %s", path)
    return path


def save_zip_to_folder(
    content: bytes,
    target_dir: Path | str,
    filename_hint: str = "download.zip",
    extract: bool = False,
    extract_dir: Optional[Path | str] = None,
) -> Path:
    """
    Salva conteúdo ZIP em disco e opcionalmente extrai.

    Retorna:
        - Caminho do arquivo .zip salvo.
    """
    zip_path = save_bytes_to_file(
        content=content,
        target_dir=target_dir,
        filename=filename_hint,
        overwrite=True,
    )

    if extract:
        dest_dir = ensure_dir(extract_dir or target_dir)
        logger.info("Extraindo %s para %s", zip_path, dest_dir)
        with ZipFile(zip_path, 'r') as zf:
            zf.extractall(dest_dir)

    return zip_path
