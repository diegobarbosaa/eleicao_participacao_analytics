```md
# Arquitetura do Projeto

Este projeto implementa um pipeline de dados inspirado no modelo Lakehouse,
com foco inicial na camada Bronze.

## Visão Geral

- Fonte: Dados públicos do TSE
- Processamento: Python + Polars
- Armazenamento: Parquet
- Metadados: DuckDB
- Execução: CLI (Typer)

## Fluxo de Dados

TSE (CSV/ZIP)
→ Downloader
→ Converter
→ Bronze (Parquet)
→ Metadata Store