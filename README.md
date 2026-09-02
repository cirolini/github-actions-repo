# github-actions-repo

Projeto de exemplo da disciplina **Cultura e Práticas DevOps e DevSecOps**
(Pós-Graduação Unisinos), usado em dois módulos:

- **Módulo 2 — Integração e Entrega Contínua:** `ci.yml` e `cd.yml`;
- **Módulo 3 — DevSecOps:** `security.yml`, `.pre-commit-config.yaml` e o SBOM.

O `security.yml` é o mesmo workflow do slide 22 do M3, com os comentários que
não cabem em um slide.

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
  security.yml    # segurança: segredos, dependências e SAST, em 3 jobs
  cd.yml          # entrega contínua: artefato + SBOM + publicação com aprovação
.pre-commit-config.yaml   # prevenção local: gitleaks, ruff e higiene de arquivos
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

## As camadas de segurança, neste repositório

O `security.yml` tem três jobs paralelos, um por camada, e todos publicam na
aba **Security** do repositório — não apenas no log da execução:

| Camada       | Onde                                    | Ferramenta                       |
| ------------ | --------------------------------------- | -------------------------------- |
| Segredos     | prevenção: `.pre-commit-config.yaml`    | Gitleaks (hook local)            |
| Segredos     | detecção: job `secrets`                 | Gitleaks (histórico completo)    |
| Dependências | job `dependencias`                      | dependency-review + `pip-audit`  |
| Código       | job `codigo`                            | CodeQL + Bandit                  |
| Inventário   | job `empacotar` do `cd.yml`             | CycloneDX (SBOM)                 |

Duas observações que valem para quem for reproduzir:

- **prevenção e detecção não se substituem.** O hook local é rápido e barato,
  mas é opcional e pode ser burlado com `git commit --no-verify`. A esteira não
  pode ser burlada, mas só age depois que o segredo já entrou no histórico — e
  aí a credencial precisa ser **rotacionada**, não basta apagar o arquivo. Por
  isso o `fetch-depth: 0` no checkout do job `secrets`: é o histórico que
  precisa ser varrido, não só o último commit.
- **em repositório público**, como este, code scanning e secret scanning são
  gratuitos. Em repositório privado seria preciso GitHub Advanced Security. As
  demais ferramentas (`gitleaks`, `pip-audit`, `bandit`, CycloneDX) funcionam
  em qualquer caso, porque rodam dentro do runner.

### SBOM: a lista de ingredientes

O `cd.yml` gera um SBOM em formato CycloneDX e o publica junto do pacote. O
log mostra a diferença que importa:

```
requirements.txt declara:
  requests==2.34.2
O SBOM lista:
  - certifi, charset-normalizer, idna, requests, urllib3
```

Uma linha declarada, cinco componentes entregues. As outras quatro vieram
junto e são igualmente sua responsabilidade. Quando sai uma CVE de `urllib3`,
a pergunta "estamos afetados?" vira uma consulta a este arquivo.

### Instalando a camada de prevenção

```bash
pip install pre-commit
pre-commit install          # uma vez por clone
pre-commit run --all-files  # para rodar sem esperar um commit
```

## Segurança da cadeia de suprimentos

Todas as actions de terceiros são fixadas por **SHA de commit**, com a versão
anotada em comentário:

```yaml
uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
```

Tags como `v7` são móveis: quem controla a action pode reapontá-las para código
malicioso, e todos os workflows que usam aquela tag passam a executá-lo. O SHA é
imutável. É a recomendação atual do GitHub para *supply chain security*.

**Há uma exceção, e é deliberada:** o `github/codeql-action` está fixado por tag
(`@v4`). A documentação do próprio GitHub recomenda a tag de major para essa
action, porque parte das funcionalidades depende de flags do lado do servidor e
uma versão antiga presa por SHA vai perdendo capacidade em silêncio. A regra
continua sendo SHA por padrão; tag apenas quando quem mantém a action pede.

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

Verificadas em setembro de 2026:

| Action | Versão | Pinagem |
|---|---|---|
| `actions/checkout` | v7.0.1 | SHA |
| `actions/setup-python` | v7.0.0 | SHA |
| `actions/upload-artifact` | v7.0.1 | SHA |
| `actions/download-artifact` | v8.0.1 | SHA |
| `gitleaks/gitleaks-action` | v3.0.0 | SHA |
| `actions/dependency-review-action` | v5.0.0 | SHA |
| `github/codeql-action` | v4 | tag (ver exceção acima) |

Hooks do pre-commit: `gitleaks` v8.30.1, `pre-commit-hooks` v6.0.0 e
`ruff-pre-commit` v0.14.2 — este último igual à versão do Ruff no
`requirements-dev.txt`, para que hook e esteira nunca discordem.

Python 3.14 e `requests` 2.34.2. Essas versões mudam com frequência — a fonte a
consultar é a página de *releases* de cada action.

## Para conduzir a aula

Veja [DEMO.md](DEMO.md) com o passo a passo da demonstração ao vivo.
