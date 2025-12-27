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

## Camadas de Dados

### Camada Bronze (Implementada ✅)

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

##### Schema de Dados (Comparecimento/Abstenção)

O schema exato pode ser consultado via CLI:

```bash
uv run participacao-eleitoral validate schema comparecimento
```

### Camada Silver (Implementada ✅)

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

#### Enriquecimento de Dados

##### Taxas Calculadas

- **TAXA_COMPARECIMENTO_PCT**: Percentual de comparecimento em relação aos aptos
- **TAXA_ABSTENCAO_PCT**: Percentual de abstenção em relação aos aptos

##### Mapeamento Geográfico

- **NOME_REGIAO**: Região geográfica do município (Norte, Nordeste, Centro-Oeste, Sudeste, Sul)

#### Validação de Qualidade

- Remoção de linhas com valores nulos
- Consistência de dados (comparecimento + abstenção = aptos)

### Lógica de Cálculo das Taxas

#### Taxa de Comparecimento

```
TAXA_COMPARECIMENTO_PCT = (QT_COMPARECIMENTO / QT_APTOS) * 100

Exemplo:
- Aptos: 100
- Compareceram: 80
- Taxa: (80/100) * 100 = 80%
```

#### Taxa de Abstenção

```
TAXA_ABSTENCAO_PCT = (QT_ABSTENCAO / QT_APTOS) * 100

Exemplo:
- Aptos: 100
- Absteram: 20
- Taxa: (20/100) * 100 = 20%

Consistência: QT_COMPARECIMENTO + QT_ABSTENCAO = QT_APTOS (em 100% dos casos)
```

### Mapeamento Geográfico

A transformação adiciona a coluna `NOME_REGIAO` baseada na coluna `SG_UF`:

| Região | UFs |
|--------|-----|
| **Norte** | AC, AP, AM, PA, RO, RR, TO |
| **Nordeste** | AL, BA, CE, MA, PB, PE, PI, RN, SE |
| **Centro-Oeste** | DF, GO, MT, MS |
| **Sudeste** | ES, MG, RJ, SP |
| **Sul** | PR, RS, SC |

**Classe Implementada:** `RegionMapper` em `src/participacao_eleitoral/silver/region_mapper.py`

### Validação de Qualidade

#### Remoção de Nulos
```
df = df.drop_nulls()

Impacto:
- Linhas_antes: quantidade antes da remoção
- Linhas_depois: quantidade após transformação
- Linhas_removidas = Linhas_antes - Linhas_depois

Logging:
- Se linhas_removidas > 0, loga warning com percentual
```

#### Validação de Schema

**Schema Físico:** `SCHEMA_SILVER` define tipos Polars para cada campo
- Garante performance e consistência
- Evita inferência errada

**Contrato Lógico:** `ComparecimentoSilverContrato` define campos obrigatórios
- Separa domínio de implementação física

**Validação:** `validar_schema_silver_contra_contrato()` garante que schema físico atende contrato
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

## Formato Parquet

### Benefícios
- Compressão eficiente
- Colunas otimizadas para leitura analítica
- Compatibilidade com múltiplas ferramentas
- Suporte a particionamento

### Estratégias de Otimização
- Particionamento por ano para consultas eficientes
- Compressão ZSTD nível 3 para equilíbrio entre tamanho e performance
- Estatísticas de colunas para otimização de consultas

## Metadados de Execução

Adicionalmente aos metadados técnicos nos arquivos Parquet, o sistema mantém:
- Histórico de execuções
- Status de processamento
- Tempo de execução
- Estatísticas de dados processados
- Informações de erro em caso de falha