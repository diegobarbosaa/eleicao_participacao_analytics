# Decisões Arquiteturais

## Armazenamento do CSV bruto

O CSV bruto é tratado como artefato temporário e removido após a conversão
para Parquet, reduzindo uso de disco e simplificando a camada Bronze.

## Idempotência

O pipeline é idempotente por padrão, utilizando metadados de ingestão
para evitar reprocessamentos desnecessários.

## Tecnologia de processamento

Polars foi escolhido devido a:
- Alto desempenho
- Tipagem explícita
- Integração nativa com Parquet