# CI/CD do Projeto

Este projeto usa GitHub Actions para garantir qualidade de código em cada push/PR.

## O que o CI Faz

- **Linting**: Ruff (análise de estilo)
- **Type Checking**: MyPy (verificação de tipos em modo strict)
- **Testes**: Pytest com coverage de código (threshold: 80%)

## Workflow: `.github/workflows/ci.yml`

### Jobs

**Quality** (paralelo):
- Lint (`ruff check src/`)
- Type Check (`python -m mypy -p participacao_eleitoral`)

**Test** (após quality passar):
- Roda apenas testes unitários (`pytest tests/unit/`)
- Gera relatório de coverage no terminal

## Executar Localmente

```bash
# Linting + Type Checking
uv run ruff check src/
uv run python -m mypy -p participacao_eleitoral

# Testes com coverage
uv run pytest tests/unit/ --cov=src --cov-report=term-missing -q
```

## Coverage

- **Threshold CI**: 80%
- **Atual**: 98% (apenas testes unitários)
- **Total**: 98 testes unitários
