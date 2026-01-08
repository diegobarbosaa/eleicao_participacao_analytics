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

## Cenários de Falha Comuns e Debugging

### Falha no Linting (Ruff)

**Erro típico:**
```
src/participacao_eleitoral/core/services.py:42:13: F401 Unused import `os`
```

**Solução:**
- Remova import não usado ou use `# noqa: F401` se necessário.
- Execute localmente: `uv run ruff check src/ --fix` para correções automáticas.

### Falha no Type Checking (MyPy)

**Erro típico:**
```
src/participacao_eleitoral/ingestion/pipeline.py:15: error: Item "None" of "Optional[str]" has no attribute "lower"
```

**Solução:**
- Adicione checagem de `None`: `if var is not None: var.lower()`
- Use `mypy --show-error-codes` para códigos detalhados.

### Falha nos Testes (Coverage Baixa)

**Erro típico:**
```
FAILED tests/unit/test_pipeline.py::test_ingestion_success - Coverage is below threshold
Coverage: 75% (threshold 80%)
```

**Solução:**
- Adicione testes para linhas não cobertas.
- Use `pytest --cov-report=html` para relatório visual.
- Exclua arquivos se não críticos: `--cov-exclude="*/test_*"`

### Falha de Rede em Dependências

**Erro típico:**
```
Failed to download uv dependencies
```

**Solução:**
- Verifique conexão; use `uv sync --offline` se cacheado.
- Limpe cache: `uv cache clean`

## Personalizando Workflows

### Adicionando Novos Jobs

Edite `.github/workflows/ci.yml`:

```yaml
jobs:
  quality:
    # ... existente
  integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: uv sync
      - run: pytest tests/integration/
```

### Ajustando Thresholds

Para coverage mais rigoroso:
```yaml
- run: pytest --cov-fail-under=90
```

### Adicionando Secrets

Para deploy:
```yaml
- name: Deploy
  run: echo ${{ secrets.DEPLOY_KEY }}
```

## Executar em Outros Ambientes

### Com Docker

```bash
docker run -v $(pwd):/app -w /app python:3.11 uv sync
docker run -v $(pwd):/app -w /app python:3.11 uv run pytest tests/unit/
```

### Apenas Quality (Sem Testes)

```bash
uv run ruff check src/
uv run python -m mypy -p participacao_eleitoral
```

### Com Relatórios Detalhados

```bash
uv run pytest tests/unit/ --cov=src --cov-report=html --cov-report=term-missing
# Abre htmlcov/index.html no navegador
```
