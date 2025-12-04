from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from hydrodata.infrastructure.file_storage import save_zip_to_folder
from hydrodata.infrastructure.http_client import HttpClient

logger = logging.getLogger("hydrodata.providers.ana")


@dataclass
class AnaClientConfig:
    """
    Configurações de acesso ao endpoint público da ANA para estações
    convencionais (séries históricas).

    Endpoint base (sem parâmetros):
        http://www.snirh.gov.br/hidroweb/rest/api/documento/convencionais

    Parâmetros principais:
        - tipo: 1 = MDB (Acess), 2 = TXT, 3 = CSV
        - documentos: lista de códigos de estações separados por ";"
    """

    base_url: str = "http://www.snirh.gov.br/hidroweb/rest/api/documento/convencionais"
    file_type: int = 3  # Ex.: 1=mdb, 2=txt, 3=csv (provavelmente irá permanecer só o csv)
    download_dir: Path = Path("data/ana/raw")


class ANAClient:
    """
    Cliente responsável por se comunicar com a API/Serviço da ANA.

    Esta classe NÃO deve conhecer detalhes da CLI nem da GUI;
    ela apenas oferece métodos de alto nível para download e
    leitura de dados da ANA.
    """

    def __init__(
        self,
        http_client: HttpClient,
        config: Optional[AnaClientConfig] = None,
    ) -> None:
        self.http_client = http_client
        self.config = config or AnaClientConfig()

    def download_station_files(
        self,
        station_codes: Iterable[int | str],
    ) -> List[Path]:
        """
        Faz o download dos arquivos brutos de uma ou mais estações
        convencionais da ANA em formato ZIP.

        Cada chamada retorna um único ZIP contendo todas as estações pedidas,
        mas, por clareza, retornamos uma lista com o caminho desse arquivo.

        NOTA:
            Este método usa o endpoint público do Hidroweb (sem autenticação),
            que pode mudar ao longo do tempo. Em produção, a recomendação
            da ANA é usar a API oficial HidroWebService (com cadastro).

        IMPORTANTE:
        Implementação ainda é esqueleto; vamos ajustar a URL e os
        parâmetros quando definirmos o endpoint real da ANA.
        """
        station_list = ";".join(str(code) for code in station_codes)
        logger.info("Solicitando download para estações: %s", station_list)

        params = {
            "tipo": str(self.config.file_type),
            "documentos": station_list
        }

        logger.debug(
            "Chamando ANA base_url=%s params=%s",
            self.config.base_url,
            params,
        )

        # Aqui usamos GET direto. Em R, às vezes faz-se um POST antes,
        # mas na prática o download do ZIP pode ser feito via GET.
        response = self.http_client.get(self.config.base_url, params=params)

        zip_filename = f"ana_{station_list}.zip"
        zip_path = save_zip_to_folder(
            content=response.content,
            target_dir=self.config.download_dir,
            filename_hint=zip_filename,
            extract=False,  # Depois podemos adicionar um flag para extrair automaticamente
        )

        logger.info("Download concluído. Arquivo salvo em %s", zip_path)
        return [zip_path]
