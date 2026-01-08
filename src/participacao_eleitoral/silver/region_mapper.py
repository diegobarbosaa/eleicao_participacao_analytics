"""Mapeamento de UFs para regiões geográficas"""


class RegionMapper:
    """Mapeia UF para região geográfica"""

    REGIAO_MAP = {
        "AC": "Norte",
        "AP": "Norte",
        "AM": "Norte",
        "PA": "Norte",
        "RO": "Norte",
        "RR": "Norte",
        "TO": "Norte",
        "AL": "Nordeste",
        "BA": "Nordeste",
        "CE": "Nordeste",
        "MA": "Nordeste",
        "PB": "Nordeste",
        "PE": "Nordeste",
        "PI": "Nordeste",
        "RN": "Nordeste",
        "SE": "Nordeste",
        "DF": "Centro-Oeste",
        "GO": "Centro-Oeste",
        "MT": "Centro-Oeste",
        "MS": "Centro-Oeste",
        "PR": "Sul",
        "RS": "Sul",
        "SC": "Sul",
        "ES": "Sudeste",
        "MG": "Sudeste",
        "RJ": "Sudeste",
        "SP": "Sudeste",
        "ZZ": "Exterior",
    }

    @classmethod
    def get_regiao(cls, uf: str) -> str:
        """
        Retorna a região geográfica baseada na UF.

        Args:
            uf: Sigla da unidade federativa

        Returns:
            Nome da região geográfica ("Exterior" para ZZ ou "Desconhecido" para outros inválidos)
        """
        return cls.REGIAO_MAP.get(uf, "Desconhecido")
