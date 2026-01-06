# Diagramas de Arquitetura

## Diagrama de Arquitetura

```mermaid
    graph TB
        subgraph "Fonte de Dados"
            TSE["TSE API / Dados Públicos / Eleitorais"]

        subgraph "Camada de Ingestão"
            CLI["CLI / Comandos Ad-hoc"]
            AF["Airflow / Orquestração"]
            DL["Downloader / HTTP/ZIP"]
            CV["Converter / CSV→Parquet"]
            TR["Transformer / Bronze→Silver"]

        subgraph "Lakehouse"
            BRZ["Bronze Layer / Parquet Files / Dados Brutos"]
            SLV["Silver Layer / Parquet Enriquecido / Taxas e Regiões"]
            GLD["Gold Layer / Planejado"]

        subgraph "Metadados"
            META["Metadata Store / DuckDB / Rastreabilidade"]

        TSE --> CLI
        TSE --> AF
        CLI --> DL
        AF --> DL
        DL --> CV
        CV --> BRZ
        TR --> SLV
        BRZ --> SLV
        SLV --> META
        SLV --> GLD

        subgraph "Core (Domínio)"
            ENT["Entidades / Dataset"]
            CNT["Contratos / Validação"]
            SRV["Services / Regras de Negócio"]

        BRZ --> ENT
        BRZ --> CNT
        SLV --> SRV

    end
```

## Diagrama de Fluxo de Dados

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Pipeline
    participant Downloader
    participant TSE
    participant Converter
    participant Transformer
    participant Storage
    participant Metadata

    User->>CLI: uv run participacao-eleitoral data ingest 2022
    CLI->>Pipeline: run(2022)

    Pipeline->>Pipeline: verificar idempotência
    Metadata-->>Pipeline: metadata (se existe)

    alt Já processado
        Pipeline-->>CLI: pular (já existe)
        CLI-->>User: mensagem de skip
    else Não processado
        Pipeline->>Pipeline: validar schema vs contrato
        Pipeline->>Downloader: download_csv(dataset, output_path)

        Downloader->>TSE: GET URL do TSE
        TSE-->>Downloader: ZIP file

        alt É ZIP?
            Downloader->>Downloader: extrair CSV
        end

        Downloader->>Downloader: calcular checksum SHA-256
        Downloader-->>Pipeline: DownloadResult / (csv_path, tamanho, checksum)

        Pipeline->>Converter: convert(csv, parquet, schema, source)

        Converter->>Storage: ler CSV com Polars
        Converter->>Converter: aplicar schema
        Converter->>Converter: adicionar colunas técnicas
        Converter->>Storage: escrever Parquet

        Converter-->>Pipeline: ConvertResult / (parquet_path, linhas)

        Pipeline->>Pipeline: remover CSV temporário

        Pipeline->>Metadata: salvar metadata(sucesso)
        Metadata-->>Pipeline: metadata salvo

        Pipeline-->>CLI: sucesso
        CLI-->>User: mensagem de sucesso
    end

    Note over User,CLI: Transformação Bronze→Silver

    User->>CLI: uv run participacao-eleitoral data transform 2022
    CLI->>Transformer: transform(bronze_parquet, silver_parquet)

    Transformer->>Transformer: verificar se bronze existe

    alt Bronze não existe
        Transformer-->>CLI: warning e skip
        CLI-->>User: mensagem de skip
    else Bronze existe
        Transformer->>Storage: ler Parquet bronze
        Transformer->>Transformer: calcular taxas (comparecimento%, abstenção%)
        Transformer->>Transformer: mapear UF → Região
        Transformer->>Transformer: remover nulos
        Transformer->>Storage: escrever Parquet silver

        Transformer-->>CLI: SilverTransformResult / (silver_path, linhas)
        CLI-->>User: mensagem de sucesso
    end
```

## Diagrama de Estrutura de Diretórios

```mermaid
graph LR
    ROOT[Project Root]

    ROOT --> SRC[src/]
    ROOT --> TESTS[tests/]
    ROOT --> AIRFLOW[airflow/]
    ROOT --> DATA[data/]
    ROOT --> DOCS[docs/]

    SRC --> CORE[core/ / domínio]
    SRC --> ING[ingestion/ / infraestrutura]
    SRC --> UTILS[utils/ / compartilhado]

    CORE --> ENT[entities.py]
    CORE --> CNT[contracts/]
    CORE --> SRV[services.py]
    CORE --> ENUM[enums.py]

    ING --> DL[downloader.py]
    ING --> CV[converter.py]
    ING --> MS[metadata_store.py]
    ING --> PL[pipeline.py]
    ING --> TF[transformer.py]

    ING --> SCHE[schemas/]

    DATA --> BRONZE[bronze/ / dados brutos]
    DATA --> SILVER[silver/ / dados enriquecidos]
    DATA --> GOLD[gold/ / métricas agregadas]

    BRONZE --> COMP[comparecimento_abstencao/]
    COMP --> YEAR[year=2014/]
    YEAR --> PARQ[data.parquet]

    SILVER --> COMP2[comparecimento_abstencao/]
    COMP2 --> YEAR2[year=2014/]
    YEAR2 --> PARQ2[data.parquet]
```

## Diagrama de Camadas de Dados

    ```mermaid
    graph TB
        subgraph "Fonte de Dados"
            TSE["TSE API / Dados Públicos / Eleitorais"]
        end

        subgraph "Camada de Ingestão"
            CLI["CLI / Comandos Ad-hoc"]
            AF["Airflow / Orquestração"]
            DL["Downloader / HTTP / ZIP"]
            CV["Converter / CSV para Parquet"]
            TR["Transformer / Bronze para Silver"]
        end

        subgraph "Lakehouse"
            BRZ["Bronze Layer / Parquet Files / Dados Brutos"]
            SLV["Silver Layer / Parquet Enriquecido / Taxas e Regiões"]
            GLD["Gold Layer / Planejado"]
        end

        subgraph "Metadados"
            META["Metadata Store / DuckDB / Rastreabilidade"]
        end
    ```
