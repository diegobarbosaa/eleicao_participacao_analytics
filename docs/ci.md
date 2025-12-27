# CI/CD do Projeto

Este documento explica como funciona a integração contínua e como resolver problemas comuns.

## Visão Geral

O CI/CD usa GitHub Actions para:
- **Linting**: Validação de código (Ruff + MyPy)
- **Testes**: Suíte completa com coverage (threshold: 80%)
- **Quality Gates**: Falha se coverage < 80% ou type errors

## Workflow Principal: `.github/workflows/ci.yml`

### Jobs

#### 1. Test Job

**Objetivo:** Garantir qualidade de código

**Steps:**
1. **Checkout**: `uses: actions/checkout@v4`
2. **Setup UV**: `uses: astral-sh/setup-uv@v7` com `enable-cache: true`
3. **Install Dependencies**: `uv sync --dev`
4. **Lint Code**: `uv run ruff check src/`
5. **Type Check**: `uv run python -m mypy -p participacao_eleitoral`
6. **Run Tests**: `uv run pytest --cov=src --cov-fail-under=80`

**Coverage Threshold:**
- **Mínimo**: 80%
- **Atual**: 98%
- **Cobertura total**: 98 testes unitários

### Trigger Events

O CI roda automaticamente em:
- `push` para branches: `main`, `develop`
- `pull_request` para branches: `main`, `develop`

### Locais de Logs

- **Workflow Runs**: Aba "Actions" no GitHub
- **Coverage**: Gera `coverage.xml` e `htmlcov/`

## Solução de Problemas

### Coverage Threshold Excedido

**Erro:**
```
ERROR: Coverage (72%) is below threshold (80%)
```

**Causa:** Novo código adicionado sem testes suficientes

**Solução:**
```bash
# Verificar cobertura por arquivo
uv run pytest --cov=src --cov-report=term-missing

# Adicionar testes para módulos com baixa cobertura
# Verificar docs/coverage/ para detalhes
```

### Type Errors (MyPy)

**Erro:**
```
ERROR: Missing type annotation in ingestion/pipeline.py:45
```

**Causa:** Funções sem type hints

**Solução:**
```python
# Adicionar type hints
from typing import Optional

def processar_dados(ano: int) -> Optional[Result]:
    # implementação
```

### Ruff Linting Errors

**Erro:**
```
ERROR: F821 undefined name 'variavel'
```

**Causa:** Variável usada antes de definição

**Solução:**
```bash
# Auto-fix
uv run ruff check --fix src/

# Ou verificar manualmente
uv run ruff check src/
```

## Referências

- [Workflow YAML](../.github/workflows/ci.yml)
- [Actions Badge](https://github.com/diegobarbosaa/eleicao_participacao_analytics/actions)
- [GitHub Actions Docs](https://docs.github.com/actions)
