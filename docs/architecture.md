# Arquitetura do Projeto

Este projeto implementa um pipeline de dados inspirado no modelo Lakehouse,
com foco inicial na camada Bronze.

## Visão Geral

- Fonte: Dados públicos do TSE
- Processamento: Python + Polars
- Armazenamento: Parquet
- Metadados: DuckDB
- Execução: CLI (Typer) e Airflow

## Componentes Arquiteturais

### 1. Camada Bronze
- **Objetivo**: Landing zone analítica para dados brutos do TSE
- **Formato**: Parquet com colunas técnicas de metadados
- **Validação**: Schema explícito com falha em inconsistência
- **Organização**: Particionada por dataset e ano

### 2. Componentes de Processamento
- **Downloader**: Gerencia downloads com retry e controle de estado
- **Converter**: Transforma dados brutos para formato analítico (Parquet)
- **Schema Validation**: Validação integrada em contratos e schemas
- **Logger**: Logging estruturado com suporte a diferentes formatos

### 3. Camada de Metadados
- **Objetivo**: Rastreabilidade e auditoria das execuções
- **Tecnologia**: DuckDB para consultas analíticas sobre metadados
- **Informações**: Timestamps, origem, checksums, status de execução

## Fluxo de Dados

```
TSE (CSV/ZIP)
    ↓
Downloader (controle de estado, retry)
    ↓
Converter (validação de schema, transformação)
    ↓
Bronze Layer (Parquet com metadados)
    ↓
Metadata Store (DuckDB - rastreabilidade)
```

## Características do Pipeline

### Idempotência
- Execuções repetidas não produzem dados duplicados
- Baseado em chave lógica (dataset + ano)
- Permite reprocessamento seguro

### Observabilidade
- Logging estruturado com contextos
- Métricas de performance
- Rastreabilidade completa

### Confiabilidade
- Tratamento explícito de erros
- Retry com estratégias configuráveis
- Validação rigorosa de dados

## Orquestração

O pipeline pode ser executado:
- Via CLI para execuções ad-hoc
- Via Airflow para execuções agendadas
- Em ambiente local ou cloud

## Escalabilidade

- Processamento paralelo com Polars
- Formato Parquet otimizado para leitura analítica
- Estrutura de particionamento eficiente