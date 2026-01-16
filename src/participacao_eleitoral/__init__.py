"""Pipeline de dados para análise de participação eleitoral do TSE.

Este pacote implementa uma arquitetura Lakehouse para processamento de dados
eleitorais, com camadas Bronze (bruto), Silver (enriquecido) e Gold (futuro).
Inclui ingestão via CLI, transformação, orquestração com Airflow e dashboard
interativo com Streamlit.

Uso principal via CLI: uv run participacao-eleitoral
"""
