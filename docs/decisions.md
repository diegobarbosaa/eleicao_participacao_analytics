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