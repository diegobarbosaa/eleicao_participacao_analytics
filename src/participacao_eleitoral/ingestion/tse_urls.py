"""Mapeamento de URLs do Portal de Dados Abertos do TSE"""


class TSEDatasetURLs:
    """Construtor de URLs para datasets do TSE"""

    BASE_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele"

    ANOS_DISPONIVEIS = [
        2024, 2022, 2020, 2018, 2016, 2014
    ]

    @classmethod
    def get_comparecimento_url(cls, ano: int) -> str:
        """Constrói URL de download de dados de comparecimento"""
        filename = f"perfil_comparecimento_abstencao_{ano}.zip"
        return f"{cls.BASE_URL}/perfil_comparecimento_abstencao/{filename}"

    @classmethod
    def listar_anos_disponiveis(cls) -> list[int]:
        """Lista todos os anos com dados disponíveis"""
        return cls.ANOS_DISPONIVEIS.copy()
