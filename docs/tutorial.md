# Tutorial: Como Executar o Projeto Eleição Participação Analytics

Este mini-tutorial guia você passo a passo para executar o pipeline de dados **eleicao_participacao_analytics** no Windows. O projeto processa dados eleitorais do TSE usando arquitetura Lakehouse (camadas Bronze, Silver, Gold).

## Introdução

O projeto ingere dados brutos do TSE (CSV), transforma em Bronze (Parquet), enriquece para Silver (taxas, regiões) e está preparado para Gold (métricas agregadas). Você pode executar via CLI (linha de comando) ou via Apache Airflow (interface web).

## Pré-requisitos

- **Python 3.11+**: Baixe em https://www.python.org. Marque "Add Python to PATH" durante instalação.
- **uv**: Gerenciador de pacotes moderno. Instale com: `pip install uv` (ou https://github.com/astral-sh/uv).
- **Git**: Para clonar o repositório (https://git-scm.com se não tiver).
- **(Opcional) Astro CLI**: Para executar Airflow (https://www.astronaut.io/docs/astro/cli/installation). Se não funcionar no Windows, use Docker Desktop.

## Instalação

1. **Clone o repositório** (se não estiver clonado):
   ```
    git clone https://github.com/diegobarbosaa/eleicao_participacao_analytics
   cd eleicao_participacao_analytics
   ```

2. **Instale dependências**:
   ```
   uv sync
   ```
   - Isso instala Polars, DuckDB, Pydantic, etc. Se falhar, tente `uv sync --dev`.

## Execução via CLI (Recomendada para Início)

Esta é a forma mais simples para desenvolvimento/testes.

1. **Navegue para o diretório do projeto**:
    Abra PowerShell ou CMD e vá para o diretório do projeto.

2. **Execute ingestão de dados** (exemplo para 2014):
   ```
   uv run participacao-eleitoral data ingest 2014
   ```
   - Baixa CSVs do TSE, valida checksums, converte para Parquet (camada Bronze).
   - Substitua 2014 por outro ano (2018, 2022, etc.).

3. **Execute transformação Silver**:
   ```
   uv run participacao-eleitoral data transform 2014
   ```
   - Calcula taxas de comparecimento/abstenção, enriquece com regiões, salva em Silver layer.

4. **Verifique saída**:
   - Dados em Parquet/DuckDB. Use `uv run participacao-eleitoral config show` para ver caminhos.

## Execução via Apache Airflow (Para Orquestração Completa)

Para usar DAGs production-ready com retry, timeout e logging.

1. **Instale Astro CLI** (se escolhido).

2. **Inicie Airflow**:
   ```
   cd airflow
   astro dev start
   ```

3. **Acesse a interface web**: http://localhost:8080
   - Execute os DAGs: `participacao_eleitoral_ingest_bronze` e `participacao_eleitoral_transform_silver`.

## Dicas Específicas para Windows

- **PATH**: Certifique-se de que Python e uv estão no PATH (reinicie o terminal após instalação).
- **Firewall/Antivírus**: Pode bloquear downloads do TSE. Desative temporariamente se houver erros de conexão.
- **Caminhos**: O projeto usa barras `/` (Unix-like). Se problemas, configure variáveis de ambiente ou use WSL.
- **Astro no Windows**: Pode não ser 100% compatível. Use Docker Desktop para rodar containers do Airflow.
- **Performance**: Para grandes datasets, aumente RAM ou use SSD.

## Exemplos de Saída Esperada

Após ingestão:
- Arquivos Parquet criados em `data/bronze/2014/`
- Metadados no DuckDB com status "success"

Após transformação:
- Dados enriquecidos em `data/silver/2014/` com colunas como `taxa_comparecimento`, `regiao`

## Solução de Problemas Comuns

- **Erro "uv não encontrado"**: Reinicie o terminal ou adicione ao PATH manualmente.
- **Falha na instalação**: `uv sync --verbose` para mais detalhes.
- **Erro de rede**: Verifique conexão com internet; TSE pode bloquear IPs.
- **Problemas com Airflow**: Use Docker: `docker run -p 8080:8080 apache/airflow:2.9.0` (adaptado).
- **Logs**: Use `uv run participacao-eleitoral --help` para comandos disponíveis.

Para mais detalhes, consulte [README.md](../README.md) ou [Arquitetura](architecture.md).

Boa sorte com o processamento dos dados eleitorais!</content>
<parameter name="filePath">docs/tutorial.md