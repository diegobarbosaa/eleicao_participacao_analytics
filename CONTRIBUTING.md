# Contribuindo ao Eleição Participação Analytics

Obrigado por interesse em contribuir! Este guia orienta como participar do desenvolvimento do projeto.

## Tipos de Contribuição

Agradecemos todos os tipos de contribuição:

- 🐛 **Bug Reports**: Identificar e reportar problemas
- 💡 **Feature Requests**: Sugerir novas funcionalidades
- 📝 **Documentação**: Melhorar docs, tutoriais, exemplos
- 🧪 **Refactoring**: Melhorar estrutura ou performance de código existente
- ✅ **Testes**: Adicionar ou melhorar testes

## Processo de Contribuição

### 1. Abra um Issue (Obrigatório para Features/Bugs)

Antes de começar a codificar, abra um issue para discutir:

**Para Bug Reports:**
- Use template de bug report (abaixo)
- Inclua passos para reproduzir
- Anexe logs/screenshots se aplicável

**Para Features:**
- Descreva o caso de uso
- Explique por que a feature seria valiosa
- Discuta implementação antes de começar

### 2. Fork e Branch

```bash
# 1. Fork o repositório
https://github.com/diegobarbosaa/eleicao_participacao_analytics/fork

# 2. Clone seu fork
git clone https://github.com/<seu-usuario>/eleicao_participacao_analytics.git
cd eleicao_participacao_analytics

# 3. Adicione upstream original
git remote add upstream https://github.com/diegobarbosaa/eleicao_participacao_analytics.git

# 4. Crie branch para sua feature
git checkout -b feature/<nome-descritivo>
```

### 3. Faça Suas Mudanças

```bash
# Instale dependências
cd eleicao_participacao_analytics
uv sync

# Crie um branch de feature
git checkout -b feature/nova-funcionalidade

# Faça as mudanças
# [desenvolva]

# Teste suas mudanças
uv run pytest
uv run ruff check src/
uv run python -m mypy -p participacao_eleitoral
```

### 4. Commit e Push

```bash
# Commit com mensagem clara
git add .
git commit -m "feat: add nova funcionalidade para cálculo de taxas regionais"

# Push para seu fork
git push origin feature/nova-funcionalidade
```

### 5. Abra um Pull Request

1. Vá para: https://github.com/diegobarbosaa/eleicao_participacao_analytics
2. Clique em "Compare & pull request"
3. Preencha o template de PR (abaixo)

## Padrões de Código

Este projeto segue padrões estritos de qualidade:

### Linting e Type Checking

```bash
# Verificar estilo de código
uv run ruff check src/ tests/

# Verificar tipos
uv run python -m mypy -p participacao_eleitoral
```

**Regras:**
- Ruff para formatação e análise de estilo
- MyPy em modo strict para type checking
- Todos os erros de lint/type devem ser resolvidos antes do PR

### Testes

```bash
# Rodar testes completos
uv run pytest --cov=src --cov-fail-under=80

# Verificar coverage
# Deve manter >= 80% (atualmente: 98%)
```

**Regras:**
- Todo novo código deve ter testes
- Cobertura mínima de 80%
- Testes de integração para fluxos E2E

### Formatação

```bash
# Formatar código automaticamente
uv run ruff format src/ tests/

# Verificar formatação
uv run ruff format --check src/ tests/
```

## Padrões de Commit

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add nova funcionalidade
fix: resolve bug X
docs: update README
refactor: optimize performance
test: add unit tests
chore: update dependencies
```

## Template de Bug Report

Ao reportar bugs, use este template:

```markdown
## 🐛 Bug Report

### Descrição
Breve descrição do problema.

### Passos para Reproduzir
1. Execute: `uv run participacao-eleitoral data ingest 2022`
2. Observe: [comportamento esperado]
3. Observe: [comportamento atual]
4. Logs/Error: [cole aqui]

### Ambiente
- Python: [3.11.x]
- OS: [Linux/Windows/Mac]
- Versão do projeto: [tag/commit]

### Comportamento Esperado
O que deveria acontecer.

### Comportamento Atual
O que está acontecendo.

### Screenshots/Logs
[Anexe aqui se aplicável]
```

## Template de Feature Request

```markdown
## 💡 Feature Request

### Motivação
Por que esta feature seria valiosa?

### Proposta
Como você imagina que a feature deveria funcionar?

### Casos de Uso
Descreva cenários onde esta feature seria usada.

### Alternativas Consideradas
Você já encontrou workarounds?

### Impacto
Quem seria beneficiado por esta feature?
```

## Template de Pull Request

```markdown
## Pull Request: [Título]

### Descrição
[Descrição detalhada das mudanças]

### Tipo de Mudança
- [ ] Bug fix
- [ ] Feature
- [ ] Refactoring
- [ ] Documentação
- [ ] Testes

### Issue Relacionado
Fixes #[número do issue]

### Mudanças
[Liste arquivos alterados]

### Testes
- [ ] Testes unitários adicionados/atualizados
- [ ] Testes de integração executados
- [ ] Testes passam localmente
- [ ] Coverage mantido >= 80%

### Checklist
- [ ] Código segue padrões de linting (Ruff)
- [ ] Código segue padrões de type checking (MyPy)
- [ ] Testes cobrem novos caminhos de código
- [ ] Documentação atualizada se necessário
- [ ] Commits seguem conventional commits
```

## Diretrizes de Code Review

### O que revisamos:

1. **Qualidade de Código**
   - Type hints presentes e corretos
   - Formatação com Ruff
   - Sem warnings de MyPy
   - Testes abrangentes

2. **Testes**
   - Cobertura >= 80%
   - Testes unitários e de integração
   - Edge cases cobertos

3. **Arquitetura**
   - Consistência com padrões existentes
   - Idempotência onde aplicável
   - Logging estruturado

4. **Documentação**
   - Docstrings em funções públicas
   - README atualizado se necessário
   - Complexidade explicada em comentários

## Processo de Review

1. Mantenedores revisam PRs em até 7 dias úteis
2. Feedback será dado via comentários no PR
3. Ajustes solicitados devem ser implementados
4. Reaplicar após ajustes para novo review
5. PRs podem ser marcados como:
   - ✅ Aprovado
   - 🔄 Requer ajustes
   - ❌ Rejeitado (com explicação)

## Perguntas Frequentes

### Q: Posso contribuir com Python diferente de 3.11?

**A:** Por enquanto o projeto requer Python >= 3.11. Contribuições compatíveis com versões anteriores podem ser aceitas se mantiverem compatibilidade.

### Q: Posso adicionar novas dependências?

**A:** Sim! Mas:
1. Justifique a necessidade
2. Use versões atuais
3. Atualize `pyproject.toml` e `uv.lock`
4. Teste antes de enviar PR

### Q: Coverage caiu após minhas mudanças. E agora?

**A:** Isso é esperado quando adiciona código novo. Você deve:
1. Adicionar testes para cobrir novo código
2. Ou adicionar comentário de `# pragma: no cover` se intencional
3. Manter threshold de 80%

## Comunicar com a Comunidade

- **GitHub Issues**: Para bugs, features, e perguntas
- **GitHub Discussions**: Para conversas mais amplas
- **LinkedIn**: [Link para seu perfil] - Comente e compartilhe o projeto!

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto (MIT).

---

**Obrigado por contribuir!** 🎉
