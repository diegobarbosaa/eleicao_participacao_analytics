# Modelo de Dados

## Camadas de Dados

## Camadas de Dados

### Camada Bronze

Os dados são armazenados em formato Parquet, organizados por dataset e ano, com particionamento eficiente para consultas analíticas.

#### Estrutura de Diretórios

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

#### Estrutura de Particionamento

- **Dataset**: Tipo de dado (ex: comparecimento_abstencao)
- **Ano**: Ano da eleição (year=2024)
- **Arquivo**: Dados em formato Parquet otimizado

#### Esquema de Dados Bronze

##### Colunas Técnicas (Metadados)

Cada arquivo Parquet contém colunas técnicas adicionais para rastreabilidade:

- `_metadata_ingestion_timestamp`: Timestamp da ingestão
- `_metadata_source`: Origem dos dados (URL do TSE)
- `_metadata_file_size`: Tamanho do arquivo original
- `_metadata_checksum`: Checksum para verificação de integridade
- `_metadata_processing_date`: Data de processamento

##### Schema de Dados (Comparecimento/Abstenção)

O schema exato pode ser consultado via CLI:

```bash
uv run participacao-eleitoral validate schema comparecimento
```

### Camada Silver (Implementada)

Dados transformados e enriquecidos para análise de participação eleitoral.

#### Estrutura de Diretórios

```
data/
└── silver/
    └── comparecimento_abstencao_silver/
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

#### Estrutura de Particionamento

- **Dataset**: Tipo de dado (ex: comparecimento_abstencao_silver)
- **Ano**: Ano da eleição (year=2024)
- **Arquivo**: Dados em formato Parquet otimizado

#### Enriquecimento de Dados

##### Taxas Calculadas

- **TAXA_COMPARECIMENTO_PCT**: Percentual de comparecimento em relação aos aptos
- **TAXA_ABSTENCAO_PCT**: Percentual de abstenção em relação aos aptos

##### Mapeamento Geográfico

- **NOME_REGIAO**: Região geográfica do município (Norte, Nordeste, Centro-Oeste, Sudeste, Sul)

#### Validação de Qualidade

- Remoção de linhas com valores nulos
- Consistência de dados (comparecimento + abstenção = aptos)

#### Lógica de Cálculo das Taxas

###### Taxa de Comparecimento

```
TAXA_COMPARECIMENTO_PCT = (QT_COMPARECIMENTO / QT_APTOS) * 100

Exemplo:
- Aptos: 100
- Compareceram: 80
- Taxa: (80/100) * 100 = 80%
```

###### Taxa de Abstenção

```
TAXA_ABSTENCAO_PCT = (QT_ABSTENCAO / QT_APTOS) * 100

Exemplo:
- Aptos: 100
- Absteram: 20
- Taxa: (20/100) * 100 = 20%
```

###### Consistência

```
QT_COMPARECIMENTO + QT_ABSTENCAO = QT_APTOS (em 100% dos casos)
```

#### Validação de Schema

**Schema Físico:** `SCHEMA_SILVER` define tipos Polars para cada campo
- Garante performance e consistência
- Evita inferência errada

**Contrato Lógico:** `ComparecimentoSilverContrato` define campos obrigatórios
- Separa domínio de implementação física
- Validação garante que schema físico atende contrato
- Falha cedo se campo obrigatório está faltando
- Protege contra mudanças silenciosas no CSV

### Metadados de Transformação

Armazenados em `silver/_metadata.duckdb`:

| Campo | Descrição |
|-------|-----------|
| `dataset` | Nome do dataset (comparecimento_abstencao_silver) |
| `ano` | Ano da eleição |
| `linhas_antes` | Quantidade antes de remoção de nulos |
| `linhas_depois` | Quantidade após transformação final |
| `duracao_segundos` | Tempo total da transformação |
| `status` | "sucesso" ou "falha" |
| `erro` | Mensagem de erro (se status="falha") |

**Idempotência:**
- Chave primária: (dataset, ano)
- UPSERT evita duplicatas
- Se arquivo já existe + status="sucesso", faz skip

### Formato Parquet

#### Benefícios

- Compressão eficiente
- Colunas otimizadas para leitura analítica
- Compatibilidade com múltiplas ferramentas
- Suporte a particionamento

#### Estratégias de Otimização

- Particionamento por ano para consultas eficientes
- Compressão ZSTD nível 3 para equilíbrio entre tamanho e performance
- Estatísticas de colunas para otimização de consultas

### Metadados de Execução

Adicionalmente aos metadados técnicos nos arquivos Parquet, o sistema mantém:

- Histórico de execuções
- Status de processamento
- Tempo de execução
- Estatísticas de dados processados
- Informações de erro em caso de falha

## Consultas de Exemplo

Use DuckDB para consultar dados analíticos diretamente dos arquivos Parquet.

### Comparação Nacional (Silver)

```sql
SELECT
    ano,
    ROUND(AVG(taxa_comparecimento_pct), 2) as taxa_comparecimento_medio,
    ROUND(AVG(taxa_abstencao_pct), 2) as taxa_abstencao_medio
FROM read_parquet('data/silver/comparecimento_abstencao_silver/year=2022/data.parquet')
GROUP BY ano
ORDER BY ano DESC;
```

### Por Região (Silver)

```sql
SELECT
    nome_regiao,
    COUNT(*) as municipios,
    ROUND(AVG(qt_comparecimento), 0) as comparecimento_medio,
    ROUND(AVG(taxa_comparecimento_pct), 2) as taxa_comparecimento_pct
FROM read_parquet('data/silver/comparecimento_abstencao_silver/year=2022/data.parquet')
GROUP BY nome_regiao
ORDER BY taxa_comparecimento_pct DESC;
```

### Top 10 Municípios por Comparecimento (Bronze)

```sql
SELECT
    nm_municipio,
    sg_uf,
    qt_comparecimento,
    qt_aptos
FROM read_parquet('data/bronze/comparecimento_abstencao/year=2022/data.parquet')
ORDER BY qt_comparecimento DESC
LIMIT 10;
```

### Metadados de Transformação

```sql
SELECT * FROM read_parquet('data/silver/_metadata.duckdb');
```

**Nota:** Para múltiplos anos, use UNION ALL ou loops em scripts Python.

## Comparação Bronze vs Silver

| Aspecto | Camada Bronze | Camada Silver |
|---------|---------------|---------------|
| **Propósito** | Landing zone bruto | Dados enriquecidos para análise |
| **Formato** | Parquet + metadados técnicos | Parquet + colunas calculadas |
| **Colunas Técnicas** | `_metadata_*` (timestamp, checksum, etc.) | `_metadata_*` + enriquecidas |
| **Dados Originais** | qt_comparecimento, qt_abstencao, qt_aptos | Mesmos + taxas calculadas |
| **Enriquecimento** | Nenhum | taxa_comparecimento_pct, taxa_abstencao_pct, nome_regiao |
| **Validação** | Schema físico vs contrato | Schema físico vs contrato + consistência |
| **Tamanho** | Compacto (dados TSE) | Levemente maior (colunas extras) |
| **Uso Típico** | Reprocessamento histórico | Dashboards, relatórios, BI |
| **Performance** | Otimizado para ingestão | Otimizado para consultas analíticas |
| **Idempotência** | Baseada em dataset+ano | Baseada em dataset+ano |
| **Dependências** | Arquivos TSE | Bronze existente + transformações |

**Escalabilidade:** Bronze suporta ~100k municípios/ano; Silver adiciona ~10-20% overhead para enriquecimento.
