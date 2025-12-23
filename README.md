# Eleição Participação Analytics

Pipeline de dados para processamento de participação eleitoral brasileira usando dados públicos do TSE (Tribunal Superior Eleitoral).

## Funcionalidades

- **Download automatizado** de dados de comparecimento eleitoral do TSE
- **Processamento eficiente** usando Polars e Parquet
- **Armazenamento estruturado** em lakehouse com DuckDB
- **Orquestração** via Apache Airflow
- **CLI completa** para operações manuais
- **Observabilidade** com logging estruturado

## Instalação

```bash
# Instalar uv (gerenciador de pacotes Python)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clonar e configurar projeto
git clone https://github.com/diegobarbosaa/eleicao_participacao_analytics.git
cd eleicao_participacao_analytics
uv sync
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

# Processar dados de um ano
uv run participacao-eleitoral data ingest 2022

# Ver configurações
uv run participacao-eleitoral utils config-show
```

## Arquitetura

O projeto segue princípios de engenharia de dados moderna:

- **Camada Bronze**: Dados brutos organizados (Parquet)
- **Contratos**: Validação de esquemas e regras de negócio
- **Idempotência**: Execuções seguras e repetíveis
- **Observabilidade**: Logs estruturados e métricas

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

## Licença

Este projeto processa dados públicos do TSE e está disponível sob licença MIT.