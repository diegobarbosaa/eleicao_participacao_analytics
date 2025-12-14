## 📌 Visão Geral

Projeto de análise de dados eleitorais baseado exclusivamente em dados públicos,
com foco no comportamento do eleitor ao longo do tempo. O objetivo principal é
compreender padrões de participação eleitoral, abstenção e sua evolução histórica,
utilizando recortes territoriais no nível de município.

O projeto não realiza previsões eleitorais, não analisa preferências partidárias
nem candidatos individuais. Seu foco é analítico, histórico e descritivo,
orientado à transparência, reprodutibilidade e governança de dados.

## 🧪 Testes

O projeto possui uma suíte de testes automatizados utilizando **pytest**,
organizada de forma a separar testes unitários e de integração.

### Estrutura dos testes

```text
tests/
├── unit/          # Testes unitários (funções e classes isoladas)
├── integration/   # Testes de integração (fluxo do pipeline e CLI)
├── data/          # Arquivos CSV usados como fixtures de teste
└── conftest.py    # Fixtures compartilhadas