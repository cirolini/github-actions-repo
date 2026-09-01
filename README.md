# github-actions-repo

Projeto de exemplo da disciplina **Cultura e Práticas DevOps e DevSecOps**
(Pós-Graduação Unisinos) — Módulo 2, Integração e Entrega Contínua.

O objetivo não é o código: é a **esteira**. O projeto é propositalmente pequeno
para que toda a atenção fique no que acontece entre o commit e a entrega.

## O que o projeto faz

Uma biblioteca Python que consulta a cotação de moedas em uma API pública e
formata o resultado no padrão brasileiro.

```bash
python -m cotacao USD-BRL
# USD-BRL: R$ 5,42 (-0,42%)
```

## Estrutura

```
.github/workflows/
  ci.yml          # integração contínua: lint, formatação e testes
  security.yml    # segurança: SAST (Bandit) e dependências (pip-audit)
  cd.yml          # entrega contínua: artefato + publicação com aprovação
src/cotacao/
  client.py       # cliente HTTP da API de cotações
  formatter.py    # formatação monetária e de variação percentual
  __main__.py     # CLI: python -m cotacao
tests/
  test_client.py     # testes do cliente, com mocks (sem rede)
  test_formatter.py  # testes das funções de formatação
```

Três arquivos de workflow, um por objetivo. É a recomendação vista em aula:
misturar CI, CD e segurança em um único YAML torna a esteira difícil de ler e
de manter.

## As sete etapas da esteira, neste repositório

| Etapa | Onde aparece |
|---|---|
| 1. Controle de versão | o próprio Git; `main` protegida pela CI |
| 2. Gatilho e servidor de CI | `on: push` / `on: pull_request` nos workflows |
| 3. Build e dependências | `setup-python` + `pip install -r requirements-dev.txt` |
| 4. Testes automatizados | `python -m unittest discover` |
| 5. Qualidade e segurança | `ruff check`, `ruff format`, `bandit`, `pip-audit` |
| 6. Artefato | `python -m build` + `upload-artifact` no `cd.yml` |
| 7. Deploy | promoção `homologacao` → `producao`, com aprovação manual |

## Rodando localmente

Antes de abrir um pull request, rode exatamente o que a esteira roda:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

ruff check .                              # análise estática
ruff format --check .                     # formatação
PYTHONPATH=src python -m unittest discover -s tests -v   # testes
```

Poder reproduzir a esteira na própria máquina é o que evita o ciclo de
"commitar para ver se passa".

## Segurança da cadeia de suprimentos

Todas as actions de terceiros são fixadas por **SHA de commit**, com a versão
anotada em comentário:

```yaml
uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
```

Tags como `v7` são móveis: quem controla a action pode reapontá-las para código
malicioso, e todos os workflows que usam aquela tag passam a executá-lo. O SHA é
imutável. É a recomendação atual do GitHub para *supply chain security*.

## Secrets

O job `secrets-demo` no `ci.yml` mostra que segredos nunca aparecem no YAML nem
no código — vêm de **Settings → Secrets and variables → Actions**. Crie um
segredo chamado `API_TOKEN` com qualquer valor e repare que, ao tentar imprimi-lo
no log, o GitHub o substitui por `***`.

## Feature flags: deploy não é release

`src/cotacao/flags.py` implementa uma flag simples. A funcionalidade de exibir o
preço de compra já está em produção, porém **desligada**:

```bash
PYTHONPATH=src python -m cotacao USD-BRL
# USD-BRL: R$ 5,42 (-0,42%)

PYTHONPATH=src COTACAO_MOSTRAR_COMPRA=true python -m cotacao USD-BRL
# USD-BRL: R$ 5,42 (-0,42%) | compra R$ 5,40
```

Mesmo binário, comportamentos diferentes, sem novo deploy. É o que separa
publicar código de ativar funcionalidade — e o que torna possível o canary e o
rollback instantâneo (basta desligar a flag).

## Entrega contínua vs. implantação contínua

O `cd.yml` tem três jobs: `empacotar` → `homologacao` → `producao`. A promoção
até homologação é automática; produção depende de um *environment* protegido.

Para ativar a aprovação manual: **Settings → Environments → New environment →
`producao` → Required reviewers**. Crie também o `homologacao`, sem revisores.

O mesmo artefato atravessa os dois ambientes, sem ser reconstruído — o job de
produção imprime o `sha256sum` do pacote para evidenciar que é o mesmo arquivo.

Com a aprovação ligada, isto é **entrega contínua**: tudo fica pronto para
publicar, mas alguém decide quando. Removendo a aprovação, vira **implantação
contínua**: o que passa nos testes vai para produção sozinho. A diferença não é
técnica — é o nível de confiança do time na própria esteira.

## Proteção da branch

Para que a esteira realmente proteja a `main`, configure em
**Settings → Branches → Add branch ruleset**:

- exigir pull request antes do merge;
- exigir que o job `Lint e testes` passe;
- exigir que a branch esteja atualizada com a `main`.

Sem isso, a CI apenas informa; com isso, ela bloqueia.

## Versões usadas

Verificadas em setembro de 2026, todas fixadas por SHA:

| Action | Versão |
|---|---|
| `actions/checkout` | v7.0.1 |
| `actions/setup-python` | v7.0.0 |
| `actions/upload-artifact` | v7.0.1 |
| `actions/download-artifact` | v8.0.1 |

Python 3.14 e `requests` 2.34.2. Essas versões mudam com frequência — a fonte a
consultar é a página de *releases* de cada action.

## Para conduzir a aula

Veja [DEMO.md](DEMO.md) com o passo a passo da demonstração ao vivo.
