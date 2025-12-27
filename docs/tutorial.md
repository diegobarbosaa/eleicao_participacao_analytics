# Tutorial de Engenharia de Dados: Pipeline de Análise de Participação Eleitoral

## Capítulo 1: Introdução ao Projeto

### O Que Este Projeto Faz

Imagine que você é um analista de dados que deseja entender os padrões de votação nas eleições brasileiras. Você precisa de dados históricos e confiáveis sobre a participação eleitoral em diferentes municípios e estados. Este projeto automatiza a coleta, processamento e armazenamento desses dados do Tribunal Superior Eleitoral (TSE).

**Visão Geral:**
- **Fonte**: Dados públicos de eleições do TSE (Tribunal Superior Eleitoral)
- **Processo**: Faz download, limpa e organiza dados de participação de votação
- **Armazenamento**: Armazena dados em formato Parquet eficiente para análise rápida
- **Resultado**: Conjuntos de dados prontos para uso para entender tendências de participação eleitoral

### Por Que Isso Importa para Engenharia de Dados

Este projeto demonstra princípios reais de engenharia de dados:
- **Confiabilidade**: Lida com falhas de rede e inconsistências de dados
- **Escalabilidade**: Processa dados de forma eficiente usando ferramentas modernas
- **Observabilidade**: Rastreia cada etapa do processamento de dados
- **Reprodutibilidade**: Mesmos dados sempre produzem os mesmos resultados

### Analogia Simples

Pense nisso como uma bibliotecária automatizada:
1. **Encontra livros** (faz download de dados do TSE)
2. **Organiza-os** (limpa e estrutura os dados)
3. **Cataloga tudo** (rastreia o que foi processado e quando)
4. **Torna fácil de encontrar** (armazena em formato otimizado para consultas)

## Capítulo 2: Compreendendo Conceitos de Engenharia de Dados

### A Pirâmide de Engenharia de Dados

A engenharia de dados segue uma abordagem em camadas, semelhante à construção de uma casa:

```
Dados Brutos (Fundação)
    ↓
Camada Bronze (Brutos mas Organizados)
    ↓
Camada Silver (Limpos e Validados)
    ↓
Camada Gold (Prontos para Negócio)
```

Este projeto implementa **Camadas Bronze e Silver**:
- **Bronze**: Tornando dados brutos confiáveis e acessíveis
- **Silver**: Enriquecendo dados para análise analítica

### Conceitos Chave Que Você Aprenderá

#### 1. ETL vs ELT
- **ETL**: Extract, Transform, Load (transforma antes de armazenar)
- **ELT**: Extract, Load, Transform (armazena primeiro, transforma depois)
- Este projeto usa **abordagem ELT** - carrega dados brutos, depois transforma conforme necessário

#### 2. Arquitetura Lakehouse
Data lakes tradicionais armazenam arquivos brutos. Data warehouses armazenam tabelas estruturadas. Lakehouse combina ambos:
- Armazenamento baseado em arquivos (flexível)
- Consulta tipo tabela (análises rápidas)
- Este projeto usa arquivos Parquet + DuckDB para consultas

#### 3. Idempotência
Uma palavra sofisticada que significa "execute várias vezes, obtenha o mesmo resultado":
```python
# Não idempotente - adiciona dados duplicados
INSERT INTO table VALUES (1, 'data')

# Idempotente - apenas insere se não existir
INSERT OR IGNORE INTO table VALUES (1, 'data')
```

#### 4. Schema-on-Read vs Schema-on-Write
- **Schema-on-Write**: Define estrutura antes de armazenar (bancos de dados)
- **Schema-on-Read**: Define estrutura ao ler (arquivos flexíveis)
- Este projeto usa **ambos** - valida esquema durante o processamento

## Capítulo 3.5: Configuração de Imports no Airflow

### O Problema

Ao executar os DAGs do Airflow, você pode encontrar este erro:

```
ModuleNotFoundError: No module named 'participacao_eleitoral.silver.pipeline'
```

Isso acontece porque o Airflow procura módulos apenas em:
- `/usr/local/airflow/dags/` (onde estão os DAGs)
- `/usr/local/lib/pythonX.Y/site-packages/` (pacotes instalados)

Mas **NÃO** em:
- `/app/src/` (onde está o código do projeto)

### A Solução

O módulo `airflow/dags/_shared.py` configurou o `sys.path` automaticamente:

```python
import sys
from pathlib import Path

# Caminho para o diretório src do projeto
# _shared.py está em airflow/dags/, então:
# - parent = airflow/dags/
# - parent.parent = airflow/
# - parent.parent.parent = raiz do projeto
project_root = Path(__file__).resolve().parent.parent.parent
src_path = project_root / "src"

# Adiciona src ao path (prioridade alta para sobrepor pacotes instalados)
sys.path.insert(0, str(src_path))
sys.path.insert(1, str(project_root))  # Para compatibilidade com código existente
```

### Por Que Isso Funciona

1. **Path Relativo Inteligente:**
   - `Path(__file__)` = `airflow/dags/_shared.py`
   - `.parent` = `airflow/dags/`
   - `.parent.parent` = `airflow/`
   - `.parent.parent.parent` = `/app/` (raiz do projeto)
   - `/app/src/` = diretório do código

2. **Prioridade Alta:**
   - `sys.path.insert(0, str(src_path))` coloca `src` no topo da lista
   - Python encontra nosso código antes de qualquer pacote instalado

3. **Único Lugar:**
   - Todos os DAGs importam `_shared` primeiro
   - O `sys.path` é configurado uma única vez
   - Funciona para Bronze e Silver

### Importando nos DAGs

**Correto (usa _shared):**
```python
from airflow.dags._shared import get_default_args, get_years_to_process

# Agora imports do projeto funcionam:
from participacao_eleitoral.silver.pipeline import SilverTransformationPipeline
```

**Errado (tentar import direto sem _shared):**
```python
# ❌ Isso falha no Airflow!
from participacao_eleitoral.silver.pipeline import SilverTransformationPipeline
```

### Executando Localmente vs Docker

**Local (Development):**
```bash
# O sys.path funciona igual em qualquer lugar
cd airflow
astro dev start
```

**Docker (Produção):**
```yaml
# No docker-compose.override.yml ou Dockerfile
services:
  airflow:
    volumes:
      - .:/app  # Monta projeto inteiro em /app
```

O path `/app/src` existe em ambos os casos.

### Por Que Não Simplesmente Instalar o Pacote?

Poderíamos instalar o pacote no ambiente Airflow:

**Dockerfile:**
```dockerfile
COPY src/ /app/src/
RUN pip install -e /app/  # Instala o pacote em modo desenvolvimento
```

**Vantagens:**
- Mais robusto (padrão Python)
- Funciona em todos os ambientes
- Permite usar imports normais em qualquer lugar

**Desvantagens:**
- Requer rebuild do Docker
- Mais complexidade de setup inicial
- Difícil em desenvolvimento iterativo

**Escolha Final:**
Configurar `sys.path` em `_shared.py` é mais simples para desenvolvimento iterativo e funciona consistentemente em todos os ambientes.

## Capítulo 4: Como o Pipeline Funciona Passo a Passo

## Capítulo 3: Visão Geral da Arquitetura do Projeto

### Arquitetura de Alto Nível

```
[API Pública do TSE]
       ↓
[Downloader] → Faz download de arquivos ZIP
       ↓
[Conversor] → CSV para Parquet
       ↓
[Camada Bronze] → Arquivos Parquet organizados
       ↓
[Armazenamento de Metadados] → Banco de dados DuckDB de rastreamento
```

### Estrutura de Diretórios

```
eleicao_participacao_analytics/
├── src/participacao_eleitoral/     # Código principal
│   ├── core/                       # Regras de negócio
│   │   ├── entities.py            # Dataset entity (aceita Bronze e Silver)
│   │   ├── services.py            # Construção de metadata Bronze
│   │   └── services_silver.py     # Construção de metadata Silver
│   ├── ingestion/                 # Processamento Bronze
│   │   ├── pipeline.py            # IngestionPipeline
│   │   ├── downloader.py         # TSEDownloader
│   │   ├── converter.py          # CSVToParquetConverter
│   │   ├── metadata_store.py     # MetadataStore (DuckDB Bronze)
│   │   ├── results.py            # DownloadResult, ConvertResult
│   │   └── tse_urls.py          # TSEDatasetURLs
│   ├── silver/                    # Processamento Silver (NOVO)
│   │   ├── pipeline.py            # SilverTransformationPipeline (NOVO)
│   │   ├── transformer.py         # BronzeToSilverTransformer
│   │   ├── metadata_store.py     # SilverMetadataStore (DuckDB) (NOVO)
│   │   ├── results.py            # SilverTransformResult (NOVO)
│   │   ├── region_mapper.py      # RegionMapper (NOVO)
│   │   └── schemas/              # Schema físico + validação (NOVO)
│   └── utils/                      # Utilitários compartilhados
├── tests/                          # Garantia de qualidade
├── airflow/                        # Orquestração
└── docs/                          # Documentação
```

### Arquitetura de Código em Três Camadas

#### 1. Camada Core (Regras de Negócio)
```python
# entities.py - O que os dados representam
@dataclass(frozen=True)
class Dataset:
    nome: str
    ano: int
    url_origem: str
```

#### 2. Camada de Infraestrutura (Detalhes Técnicos)
```python
# downloader.py - Como fazer download
class TSEDownloader:
    def download_csv(self, dataset, output_path):
        # Lógica HTTP aqui
```

#### 3. Camada de Aplicação (Orquestração)
```python
# pipeline.py - Quando e qual ordem
class IngestionPipeline:
    def run(self, ano: int):
        # Coordena tudo
```

Essa separação torna o código testável e mantível.

## Capítulo 4: Componentes Core em Detalhe

### A Entidade Dataset (Atualizado)

Pense em `Dataset` como uma "ordem de trabalho" para processamento de dados:

```python
dataset = Dataset(
    nome="comparecimento_abstencao",  # Bronze
    ano=2022,
    url_origem="https://tse.jus.br/data.zip"
)

dataset_silver = Dataset(
    nome="comparecimento_abstencao_silver",  # Silver
    ano=2022,
    url_origem="data/bronze/comparecimento_abstencao/year=2022/data.parquet"  # Path local
)
```

**Por que dataclass congelada?**
- `frozen=True`: Não pode modificar acidentalmente após criação
- `dataclass`: Gera automaticamente código boilerplate
- Type hints: IDE ajuda a capturar erros

**Validação Atualizada:**
- Validações de nome, ano e tipo de URL (HTTP ou path local)
- Suporta tanto datasets de download quanto datasets de transformação

- Validações de nome, ano e tipo de URL (HTTP ou path local)
- Suporta tanto datasets de download quanto datasets de transformação

### Componentes da Camada Silver (NOVO)

#### 1. SilverTransformationPipeline
Orquestrador que coordena todo o fluxo Bronze → Silver:

```python
from participacao_eleitoral.silver import SilverTransformationPipeline

pipeline = SilverTransformationPipeline(settings=settings, logger=logger)
pipeline.run(ano=2022)
```

**Características:**
- Idempotência (verifica DuckDB + arquivo)
- Validação de schema
- Rastreabilidade completa
- Injeção de dependência (útil para testes)

**Fluxo Interno:**
1. Cria Dataset entity
2. Verifica idempotência (se já transformou com sucesso)
3. Valida schema físico vs contrato lógico
4. Verifica se arquivo bronze existe
5. Executa transformação
6. Persiste metadados no DuckDB

#### 2. RegionMapper
Mapeia UFs brasileiras para regiões geográficas:

```python
from participacao_eleitoral.silver import RegionMapper

regiao = RegionMapper.get_regiao("SP")  # "Sudeste"
regiao = RegionMapper.get_regiao("XX")  # "Desconhecido"
```

**Características:**
- Suporta todas as 27 UFs brasileiras
- Case-sensitive (apenas siglas maiúsculas)
- Retorna "Desconhecido" para UF inválida

#### 3. Validação de Schema Silver

```python
from participacao_eleitoral.silver.schemas import validar_schema_silver_contra_contrato

validar_schema_silver_contra_contrato()  # Lança erro se schema inválido
```

Garante que o schema físico respeita o contrato lógico do domínio.

### Contratos: Acordos de Dados

Contratos definem como os dados devem ser:

```python
class ComparecimentoContrato:
    DATASET_NAME = "comparecimento_abstencao"
    CAMPOS_OBRIGATORIOS = [
        "ANO_ELEICAO",
        "QT_COMPARECIMENTO",  # Deve ter estes
    ]
```

**Analogia do mundo real**: Como um cardápio de restaurante - você sabe o que esperar.

### Gerenciamento de Configuração

Em vez de caminhos fixos, use configuração centralizada:

```python
class Settings(BaseSettings):
    data_dir: Path = Field(default_factory=lambda: Path("data"))
    request_timeout: int = 300

    # Auto-carrega de variáveis de ambiente
    model_config = SettingsConfigDict(env_prefix="PARTICIPACAO_")
```

**Benefícios**:
- Mudanças fáceis de implantação
- Nenhuma alteração de código para diferentes ambientes
- Validação evita configurações inválidas

## Capítulo 5: Como o Pipeline Funciona Passo a Passo

### Passo 1: Inicialização

```python
settings = Settings()
settings.setup_dirs()  # Cria data/, logs/, etc.

logger = ModernLogger(level="INFO", log_file="logs/pipeline.log")

pipeline = IngestionPipeline(
    settings=settings,
    logger=logger
)
```

### Passo 2: Criação do Dataset

```python
dataset = Dataset(
    nome="comparecimento_abstencao",
    ano=2022,
    url_origem=f"https://tse.jus.br/.../{ano}.zip"
)
```

### Passo 3: Verificação de Idempotência

```python
registro = metadata_store.buscar(dataset.nome, ano)
if registro and registro["status"] == "sucesso":
    logger.info("Já processado, pulando")
    return
```

**Por que importante?** Previne reprocessamento dos mesmos dados, economiza tempo e recursos.

### Passo 4: Validação de Schema

```python
validar_schema_contra_contrato()
# Garante que expectativas do código correspondem à realidade dos dados
```

### Passo 5: Fase de Download

```python
downloader = TSEDownloader(settings, logger)
download_result = downloader.download_csv(dataset, raw_csv_path)
```

**Recursos de resiliência:**
- Retry em falhas de rede
- Verificação de checksum
- Extração ZIP
- Logging de progresso

### Passo 6: Fase de Conversão

```python
converter = CSVToParquetConverter(logger)
convert_result = converter.convert(
    csv_path=download_result.csv_path,
    parquet_path=final_parquet_path,
    schema=SCHEMA_COMPARECIMENTO
)
```

**O que acontece:**
- Lê CSV com Polars (processamento de dados rápido)
- Aplica schema de tipo
- Adiciona colunas de metadados
- Escreve Parquet otimizado

### Passo 7: Armazenamento de Metadados

```python
metadata = construir_metadata_sucesso(
    dataset=dataset,
    inicio=start_time,
    fim=end_time,
    linhas=convert_result.linhas,
    # ... outras informações de rastreamento
)
metadata_store.salvar(metadata)
```

### Passo 8: Limpeza

```python
# Remove arquivo CSV temporário
raw_csv_path.unlink()
```

## Capítulo 6: Executando e Usando o Projeto

### Pré-requisitos

```bash
# Instale Python 3.11+
# Instale gerenciador de pacotes uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone e configure
git clone <repo>
cd eleicao_participacao_analytics
uv sync
```

### Executando via CLI

```bash
# Ativar ambiente
source .venv/bin/activate

# Listar anos disponíveis
uv run participacao-eleitoral data list-years

# Ingerir dados de um ano específico (Bronze)
uv run participacao-eleitoral data ingest 2022

# Transformar dados Bronze → Silver
uv run participacao-eleitoral data transform 2022

# Verificar configuração
uv run participacao-eleitoral utils config-show
```

### Executando via Airflow

```bash
# Iniciar ambiente local Airflow
cd airflow
astro dev start

# Acesse UI em http://localhost:8080
# Acione o DAG manualmente
```

### Estrutura de Saída

Após executar, você encontrará:

```
data/
├── bronze/
│   └── comparecimento_abstencao/
│       └── year=2022/
│           └── data.parquet          # Dados brutos do TSE
├── silver/
│   └── comparecimento_abstencao/
│       └── year=2022/
│           └── data.parquet          # Dados enriquecidos (taxas, regiões)
└── _metadata.duckdb                  # Histórico de processamento
```

### Consultando os Dados

```python
import duckdb

# Consultar os dados processados
conn = duckdb.connect("data/_metadata.duckdb");

# Ver o que foi processado
conn.execute("SELECT * FROM ingestao_metadata").df();

# Consultar os dados reais (Bronze)
conn.execute("""
    SELECT * FROM 'data/bronze/comparecimento_abstencao/year=2022/data.parquet'
    WHERE QT_COMPARECIMENTO > 100000
""").df();

# Consultar dados enriquecidos (Silver)
conn.execute("""
    SELECT
        NM_MUNICIPIO,
        SG_UF,
        NOME_REGIAO,
        QT_COMPARECIMENTO,
        TAXA_COMPARECIMENTO_PCT,
        TAXA_ABSTENCAO_PCT
    FROM 'data/silver/comparecimento_abstencao/year=2022/data.parquet'
    WHERE NOME_REGIAO = 'Sudeste'
    ORDER BY TAXA_COMPARECIMENTO_PCT DESC
    LIMIT 10
""").df();
```

## Capítulo 7: Explicações de Código com Melhores Práticas

### Melhor Prática 1: Injeção de Dependência

**Ruim (acoplamento forte):**
```python
class Pipeline:
    def __init__(self):
        self.logger = ModernLogger()  # Fixo
        self.downloader = TSEDownloader()  # Fixo
```

**Bom (acoplamento fraco):**
```python
class Pipeline:
    def __init__(self, logger: ModernLogger, downloader: TSEDownloader):
        self.logger = logger  # Injetado
        self.downloader = downloader  # Injetado
```

**Por quê?** Testes mais fáceis, flexibilidade, responsabilidade única.

### Melhor Prática 2: Logging Estruturado

**Ruim (declarações print):**
```python
print("Iniciando download...")
print(f"Download de {size} bytes")
```

**Bom (logging estruturado):**
```python
logger.info("download_started", url=url)
logger.success("download_completed", bytes=size, duration=5.2)
```

**Por quê?** Pesquisável, legível por máquina, formato consistente.

### Melhor Prática 3: Type Hints em Todos os Lados

**Ruim (sem tipos):**
```python
def process_data(data):
    return data
```

**Bom (com tipos):**
```python
from typing import dict

def process_data(data: dict[str, Any]) -> dict[str, Any]:
    return data
```

**Por quê?** Suporte da IDE, captura de erros cedo, código auto-documentado.

### Melhor Prática 4: Configuração Acima do Código

**Ruim (fixo):**
```python
TIMEOUT = 300
DATA_DIR = "/caminho/fixo"
```

**Bom (configurável):**
```python
class Settings(BaseSettings):
    request_timeout: int = Field(default=300)
    data_dir: Path = Field(default_factory=lambda: Path("data"))
```

**Por quê?** Configurações específicas de ambiente sem alterações de código.

### Melhor Prática 5: Princípio de Falha Rápida

**Ruim (continua em erros):**
```python
try:
    process_data()
except:
    pass  # Ignora e continua
```

**Bom (falha explicitamente):**
```python
try:
    process_data()
except Exception as e:
    logger.error("processing_failed", error=str(e))
    raise  # Pára e reporta
```

**Por quê?** Não esconde problemas, captura problemas imediatamente.

## Capítulo 8: Recursos Avançados e Configuração

### Flags de Recurso para Implementação Gradual

```python
class Settings(BaseSettings):
    enable_strict_validation: bool = False
```

**Uso:**
```bash
# Habilitar recursos experimentais
uv run participacao-eleitoral data ingest 2022 --experimental-features strict_validation
```

### Configurações Específicas de Ambiente

```bash
# Desenvolvimento
export PARTICIPACAO_ENVIRONMENT=development
export PARTICIPACAO_LOG_LEVEL=DEBUG

# Produção
export PARTICIPACAO_ENVIRONMENT=production
export PARTICIPACAO_LOG_LEVEL=WARNING
```

### Ajuste de Desempenho

```python
class Settings(BaseSettings):
    chunk_size: int = 8192  # chunks de download HTTP
    polars_threads: int = Field(default_factory=os.cpu_count)
    request_timeout: int = 300
```

## Capítulo 9: Testes e Garantia de Qualidade

### Pirâmide de Testes

```
Testes Unitários (Rápidos, muitos)     ← A maioria dos testes aqui
    ↓
Testes de Integração (Médios)
    ↓
Testes End-to-End (Lentos, poucos)
```

### Exemplo de Teste Unitário

```python
def test_dataset_validation():
    # Dataset válido
    dataset = Dataset("comparecimento_abstencao", 2022, "http://example.com")
    assert dataset.identificador_unico == "comparecimento_abstencao:2022"

    # Ano inválido
    with pytest.raises(ValueError):
        Dataset("comparecimento_abstencao", 1990, "http://example.com")
```

### Exemplo de Teste de Integração

```python
def test_full_pipeline(tmp_path):
    # Configurar diretórios temporários
    settings = Settings()
    settings.data_dir = tmp_path / "data"

    # Executar pipeline com dados mock
    pipeline = IngestionPipeline(settings=settings, logger=logger)
    pipeline.run(2022)

    # Verificar se saídas existem
    assert (settings.bronze_dir / "comparecimento_abstencao" / "year=2022" / "data.parquet").exists()
```

## Capítulo 10: Implantação e Orquestração

### Desenvolvimento Local

```bash
# Executar ano único
uv run participacao-eleitoral data ingest 2022

# Executar com logging de debug
uv run participacao-eleitoral data ingest 2022 --log-level DEBUG
```

### Orquestração Airflow

```python
# DAG executa múltiplos anos sequencialmente
YEARS_TO_PROCESS=2018,2020,2022,2024

# Cada ano executa independentemente
# Falhas não param outros anos
# Metadados impedem reprocessamento
```

### Implantação Docker

```dockerfile
FROM python:3.11-slim

# Instalar dependências
COPY pyproject.toml .
RUN pip install .

# Executar pipeline
CMD ["participacao-eleitoral", "data", "ingest", "2022"]
```

## Capítulo 11: Solução de Problemas e Melhores Práticas

### Problemas Comuns e Soluções

#### Problema 1: Timeouts de Rede
```python
# Aumentar timeout no ambiente
export PARTICIPACAO_REQUEST_TIMEOUT=600
```

#### Problema 2: Problemas de Espaço em Disco
```python
# Monitorar uso de espaço
df -h data/

# Limpar arquivos temporários
find data/ -name "*.tmp" -delete
```

#### Problema 3: Mudanças de Schema
```python
# Validar schema primeiro
uv run participacao-eleitoral validate schema comparecimento

# Verificar documentação do TSE para mudanças
```

### Monitoramento e Observabilidade

```python
# Verificar histórico de processamento
conn = duckdb.connect("data/_metadata.duckdb");
conn.execute("""
    SELECT ano, status, duracao_segundos, erro
    FROM ingestao_metadata
    ORDER BY timestamp_inicio DESC
""").df();
```

### Otimização de Desempenho

```python
# Usar múltiplos cores
export PARTICIPACAO_POLARS_THREADS=8

# Monitorar uso de memória
import psutil
print(f"Memória: {psutil.virtual_memory().percent}%")
```

## Capítulo 12: Melhorias Futuras e Simplificações

### Áreas Que Podem Ser Simplificadas

#### 1. Engenharia Excessiva em Contratos

**Atual (complexo):**
```python
class ComparecimentoContrato:
    CAMPOS_OBRIGATORIOS: ClassVar[List[str]] = [...]
    CAMPOS_VALIDACOES: ClassVar[Dict[str, Dict[str, Any]]] = {...}
```

**Alternativa simplificada:**
```python
CAMPOS_OBRIGATORIOS = ["ANO_ELEICAO", "QT_COMPARECIMENTO", "QT_ABSTENCOES"]
```

**Por que complexo?** Usa recursos avançados de Python (ClassVar, dicts aninhados) com os quais iniciantes têm dificuldade.

#### 2. Complexidade da Classe de Configuração

**Atual (Pydantic avançado):**
```python
class Settings(BaseSettings):
    data_dir: Path = Field(default=None)
    @field_validator("data_dir")
    @classmethod
    def _resolve_dirs(cls, v, info): ...
```

**Alternativa simplificada:**
```python
@dataclass
class Settings:
    data_dir: Path = Path("data")
    def __post_init__(self):
        self.data_dir.mkdir(exist_ok=True)
```

**Por que complexo?** Usa recursos avançados do Pydantic com os quais iniciantes têm dificuldade.

#### 3. Camadas de Arquitetura Abstratas

**Atual:** Separação Core/Infraestrutura com injeção de dependência

**Simplificado:** Para iniciantes, comece com funções mais simples:

```python
def process_election_year(year: int) -> None:
    """Função simples que faz tudo em um ano"""
    download_data(year)
    convert_to_parquet(year)
    save_metadata(year)
```

#### 4. Sistema de Flags de Recurso

**Atual:** Sistema complexo de flags com parsing de string

**Simplificado:** Use variáveis de ambiente diretamente:

```python
use_new_downloader = os.getenv("USE_NEW_DOWNLOADER", "false").lower() == "true"
```

### Caminho de Aprendizado Recomendado

1. **Comece Simples:** Execute os comandos CLI, entenda o fluxo básico
2. **Aprenda Conceitos Core:** ETL, Parquet, validação de dados
3. **Aprofunde:** Estude a orquestração do pipeline
4. **Avançado:** Entenda padrões arquiteturais

### Melhorias Futuras

1. **Camada Gold:** Métricas agregadas e KPIs
2. **Camada API:** API REST para acesso a dados
3. **Dashboard:** Interface web para exploração
4. **Machine Learning:** Modelos preditivos (se eticamente apropriado)
5. **Exemplos de queries:** Queries SQL com DuckDB para análise de dados

### Considerações Finais

Este projeto demonstra práticas profissionais de engenharia de dados mantendo-se educativo. A complexidade serve a necessidades do mundo real (confiabilidade, escalabilidade, manutenibilidade), mas iniciantes devem se concentrar em entender o fluxo de dados core antes de mergulhar em padrões avançados.

**Ponto Principal:** Engenharia de dados é sobre construir pipelines de dados confiáveis. Comece com scripts simples, depois adicione complexidade conforme necessário para requisitos de produção.