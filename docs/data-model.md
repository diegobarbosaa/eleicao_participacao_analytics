# Modelo de Dados

## Bronze Layer

Os dados são armazenados em formato Parquet, organizados por dataset e ano.

Exemplo de estrutura:

bronze/
└── comparecimento_abstencao/
└── year=2024/
└── data.parquet


## Metadados

Cada arquivo Parquet contém colunas técnicas adicionais:

- `_metadata_ingestion_timestamp`
- `_metadata_source`

Essas colunas permitem rastreabilidade e auditoria da ingestão.