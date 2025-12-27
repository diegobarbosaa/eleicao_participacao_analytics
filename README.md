# Eleição Participação Analytics

[![CI](https://img.shields.io/badge/CI-passing-brightgreen)](https://github.com/diegobarbosaa/eleicao_participacao_analytics/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen)](https://img.shields.io)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://img.shields.io/badge/python-3.11-blue)
[![License](https://img.shields.io/badge/license-MIT-green)](https://img.shields.io/badge/license-MIT-green)

Pipeline de dados para processamento de participação eleitoral brasileira usando dados públicos do TSE (Tribunal Superior Eleitoral).

## Funcionalidades

- **Download automatizado** de dados de comparecimento eleitoral do TSE
- **Processamento eficiente** usando Polars e Parquet
- **Transformação Bronze → Silver** com cálculo de taxas e enriquecimento geográfico
- **Armazenamento estruturado** em lakehouse com DuckDB
- **Orquestração** via Apache Airflow (ingestão e transformação)
- **CLI completa** para operações manuais
 - **Observabilidade** com logging estruturado
   - **Cobertura de testes** de 98% (98 testes unitários)
  
## Por Que Este Projeto?

### Problema Real

Dados públicos do Tribunal Superior Eleitoral (TSE) são abundantes mas **não estruturados** para análise analítica de participação eleitoral brasileira.

**Impacto Negativo:**
- Processamento manual é lento e propenso a erros
- Formatos inconsistentes (CSVs com diferentes encodings)
- Ausência de histórico e rastreabilidade
- Impossível escalar para múltiplos anos e métricas

### Solução Proposta

Este projeto implementa um **pipeline de dados moderno** inspirado em arquitetura Lakehouse, automatizando todo o fluxo de ingestão, transformação e armazenamento.

**Arquitetura Implementada:**

```
Fonte TSE (CSV) → Ingestão Automatizada
                        ↓
                 Camada Bronze (Parquet + Metadados DuckDB)
                        ↓
                 Transformação (Taxas + Regiões)
                        ↓
                 Camada Silver (Parquet Otimizado)
                        ↓
                 Camada Gold (Planejada: Métricas Agregadas)
```

**Tecnologias Modernas:**
- **ETL**: Python + Polars (10x mais rápido que Pandas)
- **Armazenamento**: Parquet (colunar format) + DuckDB (analytics engine)
- **Validação**: Pydantic (contratos de dados)
- **Orquestração**: Apache Airflow (padrão industrial)
- **CI/CD**: GitHub Actions (automated testing com coverage 98%)

### Valor de Negócio

**Para Engenheiros de Dados:**
- ✅ Demonstração de **pipeline ETL completo** (ingestão → transformação → armazenamento)
- ✅ Aplicação de **padrões modernos** (Lakehouse, idempotência, schema-first)
- ✅ **Escalabilidade**: Suporte a 10+ anos de dados (2006-2024)
- ✅ **Orquestração**: DAGs funcionais com retry, timeout e dependências

**Para Analistas:**
- ✅ Dados prontos para análise (Silver limpa e enriquecida)
- ✅ Métricas calculadas (taxas de comparecimento/abstenção)
- ✅ Contexto geográfico (mapeamento UF → Região)

**Para Organizações:**
- ✅ Processo **repetível e rastreável** (DuckDB metadados)
- ✅ **Idempotência**: Execuções seguras mesmo em caso de falha
- ✅ **Observabilidade**: Logs estruturados para debugging

### Casos de Uso

**1. Análise Histórica:**
```
"Como a taxa de comparecimento evoluiu entre 2014 e 2024 por região?"
→ Pipeline Bronze→Silver fornece dados limpos com taxas calculadas
```

**2. Monitoramento de Eleições:**
```
"Quais UFs tiveram maior abstenção em 2024?"
→ DAG Airflow agenda processamento diário de novos dados
```

**3. Métricas de Negócio:**
```
"Qual o impacto da abstenção na democracia brasileira?"
→ Camada Gold (planejada) agregará KPIs para BI dashboards
```

## CI/CD

Este projeto usa GitHub Actions para integração contínua (CI).

### Workflow Principal

O workflow `.github/workflows/ci.yml` executa automaticamente em cada push/PR:

- **Linting**: Ruff (análise de estilo) e MyPy (verificação de tipos)
- **Testes**: Pytest com cobertura de código (threshold: 80%)
- **Trigger**: Push/PR para branches `main` e `develop`

[![CI](https://github.com/diegobarbosaa/eleicao_participacao_analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/diegobarbosaa/eleicao_participacao_analytics/actions/workflows/ci.yml)

### Executar Localmente

```bash
# Rodar todo o workflow localmente
uv run pytest --cov=src --cov-fail-under=80

# Apenas linting
uv run ruff check src/
uv run python -m mypy -p participacao_eleitoral
```

### Documentação Técnica

Ver [docs/ci.md](docs/ci.md) para documentação detalhada do CI/CD, troubleshooting e resolução de problemas comuns.

## Instalação

### Pré-requisitos

- Python 3.11 ou superior
- [uv](https://github.com/astral-sh/uv) (gerenciador de pacotes)
- Git

### Opção 1: Instalação Local

```bash
# Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clonar e configurar projeto
git clone https://github.com/diegobarbosaa/eleicao_participacao_analytics.git
cd eleicao_participacao_analytics
uv sync

# Ativar ambiente virtual
source .venv/bin/activate
```

### Opção 2: Instalação Editável

```bash
# Para desenvolvimento com edição de código
uv pip install -e .
```

### Verificar Instalação

```bash
# Verificar versão do Python
python --version  # Deve ser >= 3.11

# Verificar instalação do uv
uv --version

# Rodar testes de instalação
uv run pytest tests/ -k "test_" --maxfail=1
```

## Testes

```bash
# Executar suite de testes completa
uv run pytest
```

## Uso Rápido

```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Listar anos disponíveis
uv run participacao-eleitoral data list-years

# Processar dados de um ano (Camada Bronze)
uv run participacao-eleitoral data ingest 2022

# Transformar Bronze → Silver (cálculo de taxas)
uv run participacao-eleitoral data transform 2022

# Ver configurações
uv run participacao-eleitoral utils config-show
```

### Camadas de Dados

- **Bronze**: Dados brutos do TSE em formato Parquet (download do CSV original)
- **Silver**: Dados limpos e enriquecidos com:
  - Taxas de comparecimento/abstenção (percentuais)
  - Mapeamento geográfico (UF → Região)
   - Validação de qualidade de dados (remoção de nulos)
- **Gold** (Planejada): Métricas agregadas e KPIs de negócio

## Docker e Airflow

Este projeto é compatível com Apache Airflow via Astro Runtime.

### Documentação Completa

Ver [airflow/README.md](airflow/README.md) para documentação técnica completa, incluindo:
- Inicialização do ambiente
- Estrutura de DAGs
- Troubleshooting e debugging
- Configuração e monitoramento

### Estrutura de Diretórios

```
airflow/
├── Dockerfile                  # Imagem customizada
├── docker-compose.override.yml  # Configuração local
├── dags/                       # DAGs do Airflow
│   ├── _shared.py            # Módulo compartilhado
│   └── participacao_eleitoral/
│       ├── ingest_comparecimento.py
│       └── transform_silver.py
└── src/                        # Cópia do código (carregada pelo Astro)
```

### Rodar com Astro CLI

```bash
cd airflow
astro dev start
```

Isso inicia o Airflow com os DAGs do projeto carregados automaticamente.

### DAGs Disponíveis

#### 1. Ingestão Bronze (`participacao_eleitoral_ingest_bronze`)

- Baixa dados do TSE
- Converte para Parquet
- Salva na camada Bronze

#### 2. Transformação Silver (`participacao_eleitoral_transform_silver`)

- Lê da camada Bronze
- Calcula taxas
- Enriquece geograficamente
- Salva na camada Silver

### Dockerfile

O Dockerfile foi otimizado para:
- Cache eficiente de layers (copiando dependências antes do código)
- Paths robustos (sem relativos `../`)
- Instalação rápida com pip

### Mais Detalhes

Ver documentação completa em `airflow/README.md` (a criar).

## Arquitetura

O projeto segue princípios de engenharia de dados moderna:

- **Camada Bronze**: Dados brutos organizados (Parquet)
- **Camada Silver**: Dados limpos e enriquecidos (taxas, regiões)
- **Camada Gold** (Planejada): Métricas agregadas para BI
- **Contratos**: Validação de esquemas e regras de negócio
- **Idempotência**: Execuções seguras e repetíveis
- **Observabilidade**: Logs estruturados e métricas

### Diagramas Visuais

- [Diagramas de Arquitetura](docs/architecture_diagram.md) - Representações visuais do sistema

## Desenvolvimento

```bash
# Rodar testes
uv run pytest

# Verificar qualidade de código
uv run ruff check .

# Verificar tipos
uv run mypy .
```

## Documentação

- [Tutorial Completo](docs/tutorial.md) - Guia passo a passo do projeto
- [Arquitetura](docs/architecture.md) - Decisões técnicas
- [Modelo de Dados](docs/data-model.md) - Estrutura dos dados
- [CI/CD Técnico](docs/ci.md) - Detalhes do workflow GitHub Actions
- [Airflow Integration](airflow/README.md) - Guia completo de orquestração

## Contribuindo

Agradecemos contribuições! Veja [CONTRIBUTING.md](CONTRIBUTING.md) para:
- Diretrizes de código e padrões de qualidade
- Processo de contribuição (fork → branch → PR)
- Templates para bug reports e feature requests
- Checklist para Pull Requests

## Licença

Este projeto processa dados públicos do TSE e está disponível sob licença MIT.