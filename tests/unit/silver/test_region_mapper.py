"""Testes do RegionMapper"""

from participacao_eleitoral.silver.region_mapper import RegionMapper


def test_region_mapper_mapeia_todas_ufs():
    """RegionMapper deve mapear todas as UFs corretamente."""
    mapper = RegionMapper()

    # Testar regiões
    assert mapper.get_regiao("SP") == "Sudeste"
    assert mapper.get_regiao("RJ") == "Sudeste"
    assert mapper.get_regiao("MG") == "Sudeste"
    assert mapper.get_regiao("ES") == "Sudeste"

    assert mapper.get_regiao("RS") == "Sul"
    assert mapper.get_regiao("SC") == "Sul"
    assert mapper.get_regiao("PR") == "Sul"

    assert mapper.get_regiao("AC") == "Norte"
    assert mapper.get_regiao("AP") == "Norte"
    assert mapper.get_regiao("AM") == "Norte"
    assert mapper.get_regiao("PA") == "Norte"
    assert mapper.get_regiao("RO") == "Norte"
    assert mapper.get_regiao("RR") == "Norte"
    assert mapper.get_regiao("TO") == "Norte"

    assert mapper.get_regiao("AL") == "Nordeste"
    assert mapper.get_regiao("BA") == "Nordeste"
    assert mapper.get_regiao("CE") == "Nordeste"
    assert mapper.get_regiao("MA") == "Nordeste"
    assert mapper.get_regiao("PB") == "Nordeste"
    assert mapper.get_regiao("PE") == "Nordeste"
    assert mapper.get_regiao("PI") == "Nordeste"
    assert mapper.get_regiao("RN") == "Nordeste"
    assert mapper.get_regiao("SE") == "Nordeste"

    assert mapper.get_regiao("DF") == "Centro-Oeste"
    assert mapper.get_regiao("GO") == "Centro-Oeste"
    assert mapper.get_regiao("MT") == "Centro-Oeste"
    assert mapper.get_regiao("MS") == "Centro-Oeste"


def test_region_mapper_uf_desconhecida():
    """RegionMapper deve retornar 'Desconhecido' para UF inválida."""
    mapper = RegionMapper()

    assert mapper.get_regiao("XX") == "Desconhecido"
    assert mapper.get_regiao("ZZ") == "Desconhecido"
    assert mapper.get_regiao("") == "Desconhecido"
    assert mapper.get_regiao("ABC") == "Desconhecido"


def test_region_mapper_case_sensitive():
    """RegionMapper deve ser case-sensitive."""
    mapper = RegionMapper()

    # Minúsculas não devem funcionar
    assert mapper.get_regiao("sp") == "Desconhecido"
    assert mapper.get_regiao("São Paulo") == "Desconhecido"

    # Maiúsculas corretas devem funcionar
    assert mapper.get_regiao("SP") == "Sudeste"


def test_region_mapper_mapeamento_completo():
    """RegionMapper deve ter todas as 27 UFs brasileiras."""
    mapper = RegionMapper()

    total_ufs = len(mapper.REGIAO_MAP)
    assert total_ufs == 27  # Brasil tem 26 estados + 1 DF

    # Verificar se não há duplicatas
    assert len(set(mapper.REGIAO_MAP.keys())) == total_ufs
