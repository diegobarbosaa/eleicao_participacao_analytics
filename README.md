# 📊 Participação Eleitoral

Pipeline de engenharia de dados focado na ingestão, validação e análise histórica
da participação eleitoral brasileira, utilizando exclusivamente dados públicos
disponibilizados pelo Tribunal Superior Eleitoral (TSE).

O projeto simula um ambiente real de produção, com foco em confiabilidade,
auditabilidade, reprocessamento seguro e boas práticas de arquitetura de dados.

---

## 🎯 Objetivo

Construir um pipeline idempotente e reprocessável para análise histórica de
comparecimento e abstenção eleitoral, com granularidade municipal e evolução
temporal entre diferentes pleitos.

O foco é **analítico e descritivo**, não preditivo.

---

## 🚫 Fora de escopo (decisão consciente)

Este projeto **não** contempla:

- Previsões eleitorais
- Análise de intenção de voto
- Avaliação de partidos ou candidatos
- Modelos estatísticos ou de machine learning

Essas decisões visam evitar viés político, riscos éticos e interpretações indevidas
dos dados.

---

## 🏗 Arquitetura

O projeto segue uma arquitetura **Lakehouse**, organizada em camadas bem definidas,
adaptada ao contexto de dados públicos e reprocessáveis.

- **Bronze**: camada de landing zone analítica, onde os dados públicos do TSE são
  ingeridos, validados contra contratos de dados explícitos e persistidos em
  formato columnar (Parquet). Representa o primeiro estágio persistido do pipeline.

- **Silver** *(planejado)*: camada analítica com dados modelados para exploração,
  padronização de chaves, enriquecimentos e tratamento histórico.

- **Gold** *(planejado)*: camada de métricas agregadas e indicadores de negócio,
  pronta para consumo por ferramentas de BI.

### Observações arquiteturais
- Não há persistência de camada Raw neste projeto.
- A ausência da camada Raw é uma decisão consciente, documentada em ADR,
  dado que a fonte é pública, confiável e reprocessável.
- Logs estruturados e métricas operacionais são centralizados em módulo utilitário.

---

## 🔄 Fluxo do Pipeline

1. Descoberta automática de datasets via CKAN (TSE)
2. Download controlado e versionado (Raw)
3. Validação rigorosa de schema (Bronze)
4. Persistência em formato analítico (Parquet)
5. Registro de metadados de execução

---

## 🛡 Confiabilidade e Operação

- Reprocessamento seguro por chave lógica (dataset + ano)
- Detecção de duplicidade via checksum
- Falha explícita em inconsistência estrutural
- Observabilidade via logs estruturados

---

## 🚀 Como executar

```bash
uv sync
uv run participacao-eleitoral ingest --year 2022
