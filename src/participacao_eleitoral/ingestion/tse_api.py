"""Cliente para API CKAN do TSE"""

import httpx

from participacao_eleitoral.config import Settings
from participacao_eleitoral.utils.logger import ModernLogger


class TSEApi:
    """Cliente para interagir com a API CKAN do TSE"""

    API_BASE = "https://dadosabertos.tse.jus.br/api/3"

    def __init__(self, settings: Settings, logger: ModernLogger):
        self.settings = settings
        self.logger = logger
        self.client = httpx.Client(
            timeout=self.settings.request_timeout,
            follow_redirects=True,
        )

    def get_dataset_info(self, dataset_slug: str) -> dict:
        """Obtém informações do dataset via API CKAN"""
        self.logger.debug(
            "consultando_api_ckan",
            dataset=dataset_slug,
        )

        response = self.client.get(
            f"{self.API_BASE}/action/package_show",
            params={"id": dataset_slug},
        )
        response.raise_for_status()

        data = response.json()

        if not data.get("success"):
            raise RuntimeError(f"CKAN retornou erro: {data}")

        return data["result"]

    def get_csv_resource_url(self, dataset_slug: str) -> str:
        """Obtém URL de download do CSV de um dataset"""
        dataset_info = self.get_dataset_info(dataset_slug)

        for resource in dataset_info.get("resources", []):
            if resource.get("format", "").upper() == "CSV":
                self.logger.debug(
                    "resource_csv_encontrado",
                    resource_id=resource.get("id"),
                    name=resource.get("name"),
                )
                return resource["url"]

        raise RuntimeError(f"Nenhum recurso CSV encontrado em {dataset_slug}")

    def close(self) -> None:
        self.client.close()