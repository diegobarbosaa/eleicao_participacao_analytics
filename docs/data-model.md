# Modelo de Dados

## Camada Bronze

Os dados são armazenados em formato Parquet, organizados por dataset e ano, com particionamento eficiente para consultas analíticas.

### Estrutura de Diretórios

```
data/
└── bronze/
    └── comparecimento_abstencao/
        ├── year=2014/
        │   └── data.parquet
        ├── year=2016/
        │   └── data.parquet
        ├── year=2018/
        │   └── data.parquet
        ├── year=2020/
        │   └── data.parquet
        ├── year=2022/
        │   └── data.parquet
        └── year=2024/
            └── data.parquet
```

### Estrutura de Particionamento

- **Dataset**: Tipo de dado (ex: comparecimento_abstencao)
- **Ano**: Ano da eleição (year=2024)
- **Arquivo**: Dados em formato Parquet otimizado

## Esquema de Dados Bronze

### Colunas Técnicas (Metadados)

Cada arquivo Parquet contém colunas técnicas adicionais para rastreabilidade:

- `_metadata_ingestion_timestamp`: Timestamp da ingestão
- `_metadata_source`: Origem dos dados (URL do TSE)
- `_metadata_file_size`: Tamanho do arquivo original
- `_metadata_checksum`: Checksum para verificação de integridade
- `_metadata_processing_date`: Data de processamento

### Schema de Dados (Comparecimento/Abstenção)

O schema exato pode ser consultado via CLI:

```bash
uv run participacao-eleitoral validate schema comparecimento
```

## Camadas Futuras

### Silver (Planejado)
- Dados modelados para exploração analítica
- Padronização de chaves e formatos
- Enriquecimento com dados históricos
- Tratamento de histórico e versionamento

### Gold (Planejado)
- Métricas agregadas e indicadores de negócio
- KPIs de participação eleitoral
- Prontos para consumo por ferramentas de BI

## Formato Parquet

### Benefícios
- Compressão eficiente
- Colunas otimizadas para leitura analítica
- Compatibilidade com múltiplas ferramentas
- Suporte a particionamento

### Estratégias de Otimização
- Particionamento por ano para consultas eficientes
- Compressão Snappy para equilíbrio entre tamanho e performance
- Estatísticas de colunas para otimização de consultas

## Metadados de Execução

Adicionalmente aos metadados técnicos nos arquivos Parquet, o sistema mantém:
- Histórico de execuções
- Status de processamento
- Tempo de execução
- Estatísticas de dados processados
- Informações de erro em caso de falha