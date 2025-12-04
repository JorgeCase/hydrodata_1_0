from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger("hydrodata.http")


@dataclass
class Httpresponse:
    """
    Representa uma resposta simplificada, independente da lib usada.
    """

    status_code: int
    headers: Dict[str, str]
    content: bytes


class HttpError(RuntimeError):
    """
    Erro genérico para falhas HTTP.
    """

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class HttpClient:
    """
    Interface simples para um cliente HTTP.
    Outras implementações devem sobrescrever os métodos.
    """

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
    ) -> Httpresponse:
        raise NotImplementedError


class RequestsHttpClient(HttpClient):
    """
    Implementação real usando requests.Session.
    """

    def __init__(self, default_timeout: int = 30) -> None:
        self._session = requests.Session()
        self._session.headers.update(
            {"User-Agent": "hydrodata/0.1 (ANA/INMET data downloader)"}
        )

        token = os.getenv("ANA_API_TOKEN")
        if token:
            self._session.headers.update({"Authorization": f"Bearer {token}"})

        self._default_timeout = default_timeout

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> Httpresponse:
        real_timeout = timeout or self._default_timeout
        logger.debug("Http GET %s params=%s timeout=%s", url, params, real_timeout)

        try:
            resp = self._session.get(
                url,
                params=params,
                timeout=real_timeout,
            )
        except requests.RequestException as exc:
            logger.error("Erro de conexão HTTP: %s", exc)
            raise HttpError(f"Erro de conexão ao acessar {url}") from exc

        logger.debug("Resposta HTTP %s status=%s", url, resp.status_code)

        if resp.status_code >= 400:
            # Aqui podem ser refinadas mensagens específicas caso necessário.
            msg = f"Erro HTTP {resp.status_code} ao acessar {url}"
            logger.error(msg)
            raise HttpError(msg, status_code=resp.status_code)

        return Httpresponse(
            status_code=resp.status_code,
            headers=dict(resp.headers),
            content=resp.content,
        )


class RecordingHttpClient(HttpClient):
    """
    Cliente HTTP que grava/resgata respostas em disco.

    Estratégia:
        - Gera uma chave única a partir de ({)url + params).
        - Se já existir um arquivo gravado para essa chave -> lê e devolve.
        - Se não existir -> chama o cliente real, grava a resposta (200),
        e devolve.
    """

    def __init__(
        self,
        inner: HttpClient,
        record_dir: Path | str = "data/http_records",
    ) -> None:
        self._inner = inner
        self._record_dir = Path(record_dir)
        self._record_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("RecordingHttpClient usando pasta: %s", self._record_dir)

    def _make_key(
        self,
        url: str,
        params: Optional[Dict[str, Any]],
    ) -> str:
        raw = json.dumps({"url": url, "params": params}, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def record_path(self, key: str) -> Path:
        return self._record_dir / f"{key}.bin"

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Httpresponse:
        key = self._make_key(url, params)
        path = self.record_path(key)

        if path.exists():
            logger.info("Reutilizando resposta gravada para %s (key=%s)", url, key)
            content = path.read_bytes()
            # Poderíamos salvar headers em separado se for necessário.
            return Httpresponse(status_code=200, headers={}, content=content)

        logger.info("Nenhum mock para %s. Fazendo requisição real.", url)
        resp = self._inner.get(url, params=params, timeout=timeout)

        if resp.status_code == 200:
            logger.debug("Gravando resposta de %s em %s", url, path)
            path.write_bytes(resp.content)
        else:
            logger.warning(
                "Resposta não 200 (%s) não será gravada (url=%s)",
                resp.status_code,
                url,
            )

        return resp
