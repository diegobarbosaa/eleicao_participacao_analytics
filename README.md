# Eleição Participação Analytics

[![CI](https://img.shields.io/badge/CI-passing-brightgreen)](https://github.com/diegobarbosaa/eleicao_participacao_analytics/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen)](https://img.shields.io)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://img.shields.io/badge/python-3.11-blue)
[![License](https://img.shields.io/badge/license-MIT-green)](https://img.shields.io/badge/license-MIT-green)

Pipeline de dados production-ready para ingestão, transformação e orquestração de dados eleitorais do TSE usando arquitetura Lakehouse.

## Stack Tecnológica

### Core ETL
- **Python 3.11+** | **Polars** (engine analítica 10x mais rápida que Pandas)
- **Pydantic** (validação de schemas) | **DuckDB** (metadados analíticos)
- **PyArrow** (Parquet/CSV I/O) | **Tenacity** (retry strategies)

### Orquestração & Infra
- **Apache Airflow** (DAGs production-ready com retry, timeout, SLAs)
- **Docker** | **Astro Runtime** (Airflow-as-Code)
- **GitHub Actions** (CI/CD automatizado com cache de dependências)

### Qualidade de Código
- **98% coverage** | **98 testes unitários** (Pytest)
- **Ruff** (linting) | **MyPy** (strict type checking)
- **Schema-first design** | **Idempotência** | **Observabilidade**

## Arquitetura

Implementa **Lakehouse pattern** com multi-camada:

```
TSE (CSV) → Ingestão → Bronze (Parquet + DuckDB)
                      → Silver (Enriquecido + Taxas + Regiões)
                      → Gold (Planejado: Métricas Agregadas)
```

**Camadas:**
- **Bronze:** Landing zone com dados brutos estruturados
- **Silver:** Dados limpos, enriquecidos (taxas de comparecimento/abstenção, UF→Região)
- **Gold:** Métricas agregadas para BI dashboards

## Funcionalidades Principais

✅ **Ingestão Production-Ready:** Download automatizado de CSVs do TSE com retry, validação de checksum e conversão para Parquet

✅ **Transformação Bronze→Silver:** Cálculo de taxas percentuais, limpeza de nulos, enriquecimento geográfico (RegionMapper UF→Região)

✅ **Orquestração Airflow:** DAGs funcionais com idempotência (DuckDB), retry exponencial, timeout e logging estruturado

✅ **Metadados DuckDB:** Rastreabilidade completa de execuções (dataset, ano, status, linhas, duração, checksum)

✅ **CLI Completa:** Interface Typer para operações manuais (ingest, transform, config-show)

## Qualidade & Testes

- **98% coverage** com 98 testes unitários (threshold CI: 80%)
- **CI/CD automatizado:** linting + type checking + testes em cada push/PR
- **Schema validation:** Pydantic contracts para garantir qualidade de dados
- **Idempotência:** Execuções seguras mesmo em caso de falha (UPSERT por dataset+ano)
- **Observabilidade:** Logs estruturados com contexto (Rich terminal)

## Quick Start

```bash
git clone <repo>
cd eleicao_participacao_analytics
uv sync

# Ingestão + transformação Bronze→Silver
uv run participacao-eleitoral data ingest 2014
uv run participacao-eleitoral data transform 2014
```

## Orquestração Airflow

**DAGs Production-Ready:**
- `participacao_eleitoral_ingest_bronze`: Ingestão de dados do TSE
- `participacao_eleitoral_transform_silver`: Transformação com cálculo de taxas

```bash
cd airflow
astro dev start  # Airflow UI: http://localhost:8080
```

**Arquitetura dos DAGs:**
- Idempotência via DuckDB (verifica metadados antes de processar)
- Retry exponencial (3 tentativas com backoff)
- Timeout (30 min por task)
- Logging estruturado para debugging

## Estrutura do Projeto

```
src/
├── ingestion/      # Pipeline Bronze (downloader, converter, metadata_store)
├── silver/        # Pipeline Silver (transformer, region_mapper)
├── core/          # Domínio (entities, contracts, enums, services)
└── utils/         # Logger estruturado, Settings (Pydantic)

tests/             # 98 testes unitários + testes de integração
airflow/dags/      # DAGs production-ready
```

## Documentação Técnica

- **[Arquitetura](docs/architecture.md)** - Decisões técnicas e design
- **[Modelo de Dados](docs/data-model.md)** - Estrutura das camadas Bronze/Silver/Gold
- **[Decisões Arquiteturais](docs/decisions.md)** - ADRs (Architecture Decision Records)
- **[Airflow](airflow/README.md)** - Configuração e uso

## Licença

MIT

---

**Recrutadores:** Este é um projeto production-ready que demonstra domínio de Python moderno, engenharia de dados, orquestração com Airflow, e qualidade de código (98% coverage, CI/CD, type checking).
