```md
# Registros de Decisão Arquitetural (ADR)

Este documento registra decisões arquiteturais relevantes tomadas ao longo
do desenvolvimento do projeto.

---

## ADR-001 – Arquitetura Lakehouse

Optamos por uma arquitetura Lakehouse para permitir:
- Separação clara entre dados brutos e analíticos
- Reprocessamento seguro
- Evolução incremental do modelo de dados

---

## ADR-002 – Pipeline Idempotente

O pipeline deve ser idempotente por:
- dataset
- ano eleitoral
- versão de schema

Execuções duplicadas não devem gerar dados inconsistentes.

---

## ADR-003 – Uso de Parquet como formato analítico

Parquet foi escolhido por:
- Eficiência em leitura analítica
- Compressão
- Compatibilidade com ferramentas de BI e engines SQL

---

## ADR-004 – Falhar cedo em quebra de schema

Preferimos falhar explicitamente a ingerir dados inconsistentes.
Quebras de schema são tratadas como erro fatal.

---

## ADR-005 – Não realizar previsões eleitorais

Decidimos não implementar modelos preditivos para evitar:
- Viés político
- Riscos éticos e legais
- Interpretações indevidas dos dados

O projeto tem foco exclusivamente histórico e descritivo.

---

## ADR-006 – Dados públicos apenas

Somente dados públicos, auditáveis e reproduzíveis são utilizados,
garantindo transparência e reprodutibilidade.

---

## ADR-007 – Centralização de logging em módulo utilitário

O logging da aplicação é centralizado no módulo `utils`,
garantindo padronização e fácil integração com sistemas de observabilidade.

---

## ADR-008 – Uso de Polars e DuckDB no Lakehouse

As transformações analíticas são realizadas em Python utilizando Polars,
priorizando performance e clareza de código.

DuckDB é utilizado como engine analítica para consultas SQL sobre arquivos
Parquet, criação de views e validações, sem atuar como banco transacional.

Essa abordagem reflete arquiteturas modernas de Lakehouse file-based.

---

## ADR-009 – Uso de Airflow com Astronomer e Docker

O projeto utiliza Apache Airflow empacotado via Astronomer,
executando em containers Docker.

Essa escolha visa:
- Padronização de ambiente
- Facilidade de deploy em cloud
- Simulação de ambientes produtivos reais

A infraestrutura é introduzida de forma incremental,
evitando complexidade prematura.

---

## ADR-010 – Implementação de Camada Silver

Optamos por implementar uma camada de transformação Silver para:
- Enriquecer dados brutos da camada Bronze
- Calcular métricas derivadas (taxas de participação)
- Adicionar contexto geográfico (mapeamento UF → Região)
- Facilitar análises analíticas futuras

### Transformações Implementadas

1. **Cálculo de Taxas**
   - `TAXA_COMPARECIMENTO_PCT`: (comparecimento / aptos) * 100
   - `TAXA_ABSTENCAO_PCT`: (abstenção / aptos) * 100

2. **Mapeamento Geográfico**
   - UF → Região (Norte, Nordeste, Centro-Oeste, Sudeste, Sul)

3. **Validação de Qualidade**
   - Remoção de linhas com valores nulos
   - Garantia de consistência dos dados

### Orquestração

A transformação é orquestrada separadamente da ingestão Bronze:
- DAG independente: `participacao_eleitoral_transform_silver`
- Validação de dependência: Bronze deve existir antes da transformação
- Idempotência: Não reprocessa se Silver já existe

### Benefícios

- Separação clara de responsabilidades (ingestão vs transformação)
- Reutilização da camada Bronze para múltiplas transformações
- Facilidade de adicionar novos enriquecimentos no futuro

---

## ADR-011 – Consistência Bronze ↔ Silver

**Contexto:**
A camada Silver foi implementada após Bronze, necessitando garantir consistência de estilo, estrutura e boas práticas entre as duas camadas da arquitetura Medallion.

**Decisão:**
Adotar padrões consistentes entre Bronze e Silver em todos os aspectos de engenharia de dados:

### 1. Orquestração

**Bronze:** `IngestionPipeline`
**Silver:** `SilverTransformationPipeline`

- Ambos seguem mesmo padrão de docstring ("Esta classe:" / "NÃO:")
- Ambos aplicam injeção de dependência (logger, metadata_store)
- Ambos coordenam etapas, transformações e persistência

**Benefícios:**
- Novos desenvolvedores entendem padrão rapidamente
- Código mais fácil de manter e testar

### 2. MetadataStore com DuckDB

**Bronze:** `MetadataStore` (metadados de ingestão)
**Silver:** `SilverMetadataStore` (metadados de transformação)

**Padrões Comuns:**
- Ambos usam DuckDB para rastreabilidade
- Chave primária: (dataset, ano)
- UPSERT para idempotência
- Métodos: salvar(), buscar(), listar_todos()

**Diferenças:**
- Bronze: campos como checksum, file_size, source (download)
- Silver: campos como linhas_antes, linhas_depois (transformação)

**Benefícios:**
- Auditoria completa de todas as execuções
- Idempotência robusta em ambas as camadas
- Observabilidade consistente

### 3. Schema Físico + Validação

**Bronze:**
- `SCHEMA_COMPARECIMENTO` + `validar_schema_contra_contrato()`

**Silver:**
- `SCHEMA_SILVER` + `validar_schema_silver_contra_contrato()`

**Padrões Comuns:**
- Schema físico define tipos Polars para cada campo
- Validação garante que schema físico atende contrato lógico
- Falha cedo se inconsistência encontrada

**Benefícios:**
- Protege domínio contra mudanças silenciosas
- Documentação clara de expectativas de dados
- Facilidade de debug

### 4. Lazy Evaluation com Polars

**Bronze e Silver:** `pl.scan_parquet()` em vez de `pl.read_parquet()`

**Benefícios:**
- Melhor performance em arquivos grandes
- Otimizações automáticas do Polars
- Menor uso de memória

### 5. Result Objects

**Bronze:** `DownloadResult`, `ConvertResult`
**Silver:** `SilverTransformResult`

**Padrões Comuns:**
- Todos são `@dataclass(frozen=True)`
- Imutabilidade previne bugs
- Clara separação entre input/output

**Benefícios:**
- Código mais previsível
- Fácil teste de output
- Type hints automáticos

### 6. Estrutura de Arquivos

**Bronze (9 arquivos):**
```
ingestion/
├── __init__.py           # Com __all__
├── pipeline.py
├── downloader.py
├── converter.py
├── metadata_store.py
├── results.py
├── tse_urls.py
└── schemas/
    ├── __init__.py       # Com __all__
    └── comparecimento.py
```

**Silver (8 arquivos):**
```
silver/
├── __init__.py           # Com __all__
├── pipeline.py
├── transformer.py
├── results.py
├── metadata_store.py
├── region_mapper.py
└── schemas/
    ├── __init__.py       # Com __all__
    └── comparecimento_silver.py
```

**Padrões Comuns:**
- __all__ em todos os __init__.py
- results.py separado
- metadata_store.py separado
- schemas/ separado

**Benefícios:**
- Estrutura previsível
- Fácil navegação
- Separação clara de responsabilidades

### 7. Core Services

**Bronze:** `services.py`
- `construir_metadata_sucesso()`
- `construir_metadata_falha()`

**Silver:** `services_silver.py`
- `construir_metadata_silver_sucesso()`
- `construir_metadata_silver_falha()`

**Benefícios:**
- Separação de domínio vs infra
- Fácil testes de serviços
- Consistência de metadata entre camadas

### 8. DAG Padrão

**Bronze:** Usa `IngestionPipeline` direto
**Silver:** Usa `SilverTransformationPipeline` direto

**Padrões Comuns:**
- DAG chama pipeline.run(ano)
- Pipeline cuida de toda a lógica
- Idempotência é verificada internamente

**Benefícios:**
- DAG simples e focado
- Fácil testar pipeline isoladamente
- Consistência de orquestração

### Trade-offs

**Custo:**
- Mais arquivos (maior superfície de código)
- Duplicação de padrões (mas intencional)

**Benefícios:**
- Consistência clara entre camadas
- Código mais fácil de aprender e manter
- Testes mais previsíveis
- Menos "surpresas" arquiteturais

**Decisão Final:**
A consistência entre Bronze e Silver supera o custo de arquivos adicionais. Padrões claros ajudam novos desenvolvedores e reduz bugs causados por inconsistências.

---

## ADR-012 – Configuração de sys.path para Imports no Airflow

**Contexto:**
O Airflow executa DAGs a partir do diretório `dags/`, mas o código do projeto está em `src/`. Isso causava erros de import quando os DAGs tentavam importar módulos do projeto.

**Erro Encontrado:**
```
ModuleNotFoundError: No module named 'participacao_eleitoral.silver.pipeline'
```

**Isso acontece porque o Airflow procura módulos apenas em:**
- `/usr/local/airflow/dags/` (onde estão os DAGs)
- `/usr/local/lib/pythonX.Y/site-packages/` (pacotes instalados)

**Mas NÃO em:**
- `/app/src/` (onde está o código do projeto)

**Decisão:**
Configurar `sys.path` no módulo compartilhado `_shared.py` para adicionar `src/` ao Python path antes dos imports do projeto.

**Implementação:**
```python
# Em airflow/dags/_shared.py
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

**Benefícios:**
1. ✅ Configuração centralizada em um único lugar (`_shared.py`)
2. ✅ Funciona para todos os DAGs (Bronze e Silver)
3. ✅ Funciona tanto em desenvolvimento local quanto em Docker
4. ✅ Todos os DAGs importam `_shared` primeiro (padrão consistente)
5. ✅ Não requer alteração de variáveis de ambiente ou Dockerfile

**Trade-offs:**
1. ⚠️ Manipulação de `sys.path` é considerada "non-Pythonic"
2. ⚠️ Pode confundir desenvolvedores novatos
3. ✅ Mas é o padrão recomendado para projetos Airflow com estrutura monorepo

**Alternativas Consideradas:**
1. ✅ **Escolhida:** `sys.path` em `_shared.py` (centralizado, simples)
2. ❌ Variável de ambiente `PYTHONPATH` (difícil de configurar em Docker)
3. ❌ Modificar `Dockerfile` para instalar pacote (requer rebuild)
4. ❌ Adicionar path em cada DAG individual (repetição de código)

**Por Que Isso Funciona:**
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

**Importando nos DAGs:**
```python
from airflow.dags._shared import get_default_args, get_years_to_process

# Agora imports do projeto funcionam:
from participacao_eleitoral.silver.pipeline import SilverTransformationPipeline
```

**Executando Localmente vs Docker:**
```bash
# Local (Development)
cd airflow
astro dev start
# O sys.path funciona igual em qualquer lugar

# Docker (Produção)
# No docker-compose.override.yml:
services:
  airflow:
    volumes:
      - .:/app  # Monta projeto inteiro em /app
```

O path `/app/src` existe em ambos os casos.

**Por Que Não Simplesmente Instalar o Pacote?**

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

**Decisão Final:**
Apesar de `sys.path` não ser idiomático, é a melhor solução para Airflow com projetos monorepo. A configuração centralizada em `_shared.py` reduz complexidade e funciona consistentemente em todos os ambientes.
```
