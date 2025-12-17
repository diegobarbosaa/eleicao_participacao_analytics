```md
# Architectural Decision Records (ADR)

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