# Roteiro de demonstração em aula

Duas sequências independentes, uma por módulo:

| Parte | Módulo | Atos | Tempo |
| ----- | ------ | ---- | ----- |
| A — a esteira entrega | M2 · CI/CD (slides 20 a 24) | 1 a 8 | 12 a 15 min |
| B — a esteira protege | M3 · DevSecOps (slides 20 a 24) | 9 a 13 | 12 a 15 min |

Cada parte se sustenta sozinha. Se as aulas forem em dias diferentes, comece
a Parte B pelo Ato 9, que retoma o contexto em um minuto.

---

## Antes da aula

**Para a Parte A (M2):**

1. Faça o push inicial e confirme que a aba **Actions** está verde.
2. Ligue a proteção da branch (`Settings → Branches`), exigindo o job
   `Lint e testes` — sem isso a demonstração do bloqueio não funciona.
3. Deixe duas abas abertas: o repositório e a aba Actions.

**Para a Parte B (M3):**

4. Rode o workflow **Segurança** ao menos uma vez e confirme que a aba
   **Security → Code scanning** já tem resultados. Na primeira execução o
   CodeQL demora alguns minutos; não faça isso ao vivo.
5. Este repositório é **público**, então CodeQL e secret scanning são
   gratuitos. Em repositório privado seria necessário o GitHub Advanced
   Security — vale avisar a turma, porque muitos vão tentar em repo privado.
6. Instale o pre-commit na sua máquina: `pip install pre-commit && pre-commit install`.

---

# Parte A — a esteira entrega (Módulo 2)

## Ato 1 — A esteira verde (3 min)

Abra a aba **Actions** e mostre a execução mais recente.

Pontos a destacar:

- os três workflows aparecem separados, cada um com seu objetivo;
- o CI rodou em três versões de Python ao mesmo tempo (a matriz);
- clique em um job e abra os logs: cada step é uma linha do YAML.

> Pergunta para a turma: quanto tempo essa validação levaria manualmente?

---

## Ato 2 — Quebrando o lint (4 min)

Crie a branch e introduza um erro de padrão:

```bash
git checkout -b demo/quebra-lint
```

Em `src/cotacao/formatter.py`, adicione um import que não será usado.
Insira **depois** da linha `from __future__ import annotations`, deixando uma
linha em branco antes:

```python
import os
```

(Se colocar antes do `from __future__`, o Ruff acusa três erros em vez de um e
a demonstração fica confusa.)

```bash
git commit -am "demo: import nao utilizado"
git push -u origin demo/quebra-lint
```

Abra o pull request e mostre:

- o check fica **vermelho em segundos**, antes de qualquer humano revisar;
- o Ruff aponta arquivo, linha e o código da regra (`F401`);
- com a branch protegida, o botão de merge fica **bloqueado**.

> O ponto pedagógico: ninguém precisou avisar o time. A esteira avisou.

---

## Ato 3 — Quebrando um teste (4 min)

No mesmo PR, altere a regra de negócio em `formatter.py`:

```python
# de:
sinal = "+" if pct > 0 else ""
# para:
sinal = "+"          # passa a colocar "+" até em variação negativa
```

```bash
git commit -am "demo: sinal sempre positivo"
git push
```

Mostre o log do teste que falhou:

```
AssertionError: '+-0,42%' != '-0,42%'
```

Destaque que o teste descreve o **comportamento esperado**: a mensagem de erro
já explica o que quebrou, sem depurar nada.

---

## Ato 4 — Consertando (2 min)

Reverta as duas mudanças e faça o push:

```bash
git revert --no-edit HEAD HEAD~1
git push
```

A esteira roda de novo e fica verde. O merge é liberado.

> Feche o arco: o valor não está em impedir o erro, e sim em descobri-lo em
> minutos — e não no dia do release.

---

## Ato 5 — Entrega contínua e promoção de artefato (3 min)

Na aba Actions, dispare o **CD** manualmente (`Run workflow`).

Mostre a cadeia dos três jobs:

- `empacotar` roda sozinho, valida e gera o artefato;
- `homologacao` promove automaticamente — sem aprovação;
- `producao` fica **aguardando aprovação** (Review deployments).

Abra o log de produção e mostre o `sha256sum`: é o **mesmo pacote** que passou
por homologação, não uma reconstrução.

> Aqui fica visível a diferença entre entrega e implantação contínua: a esteira
> deixou tudo pronto, mas quem decide publicar é uma pessoa. Tirar o bloco
> `environment` do job de produção transforma entrega em implantação contínua.

---

## Ato 6 — Secrets (2 min)

Antes da aula, crie em **Settings → Secrets and variables → Actions** um segredo
chamado `API_TOKEN` com qualquer valor (por exemplo `abc123xyz`).

Abra o job **Secrets (demonstração)** da execução mais recente do CI. O log mostra
o comprimento do token e, ao tentar imprimi-lo, exibe `***`.

> Dois pontos: o segredo não está no código nem no YAML, e o GitHub mascara o
> valor no log automaticamente. Mas cuidado — mascaramento não é criptografia:
> quem tem permissão de editar workflows consegue exfiltrar segredos. Por isso
> `permissions: contents: read` e revisão de mudanças em `.github/workflows`.

---

## Ato 7 — Feature flag: deploy não é release (3 min)

No terminal, com o projeto local:

```bash
PYTHONPATH=src python -m cotacao USD-BRL
# USD-BRL: R$ 5,42 (-0,42%)

PYTHONPATH=src COTACAO_MOSTRAR_COMPRA=true python -m cotacao USD-BRL
# USD-BRL: R$ 5,42 (-0,42%) | compra R$ 5,40
```

Mesmo código, mesmo artefato, comportamentos diferentes — sem novo deploy.

> Amarre com o slide 26: a funcionalidade já está em produção, desligada. Ligar
> vira decisão de produto, não de engenharia. É também o rollback mais rápido
> que existe: desligar a flag não exige deploy nenhum.

---

## Ato 8 — Pinagem por SHA (2 min, opcional)

Abra qualquer workflow e mostre a linha:

```yaml
uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
```

> Pergunta para a turma: por que não simplesmente `@v7`? Porque tags são móveis.
> Quem controla a action pode reapontar `v7` para código malicioso, e todos os
> workflows do mundo que usam essa tag passam a executá-lo no próximo run. O SHA
> é imutável. O comentário ao lado preserva a legibilidade da versão.

---

# Parte B — a esteira protege (Módulo 3)

Esta parte casa com a Seção 4 do M3 (slides 20 a 24). O arquivo
`.github/workflows/security.yml` é **o mesmo workflow do slide 22**, com os
comentários que não cabem no slide. Projete o slide, depois abra o arquivo.

---

## Ato 9 — Do slide para o repositório (2 min)

Logo depois da atividade em duplas do slide 24, abra o `security.yml` no
GitHub e mostre que é o mesmo YAML que eles acabaram de ler.

Percorra os três jobs e amarre com o que já foi respondido:

- `secrets`, `dependencias`, `codigo` — as três camadas;
- eles rodam **em paralelo** porque são independentes: nenhum precisa do
  resultado do outro;
- `permissions: security-events: write` no topo é o que autoriza publicar.

> Uma diferença proposital em relação ao slide: aqui o `if` de pull request
> está no *step* da `dependency-review`, não no job inteiro. Motivo: o
> `pip-audit` do mesmo job precisa continuar rodando no agendamento de
> segunda-feira. Boa pergunta para a turma — por que essa distinção importa?

---

## Ato 10 — A aba Security (3 min)

Abra **Security → Code scanning**. É o momento mais importante da aula.

Mostre que cada achado tem severidade, arquivo, linha, e um botão para
dispensar com justificativa. Filtre por ferramenta e mostre que há **duas**
fontes: `CodeQL` e `bandit`.

> Aqui fecha o slide 23: as duas ferramentas falam SARIF, então publicam no
> mesmo lugar. O time olha uma tela, não duas. E compare com o log da
> execução: no log, o achado some na próxima run; aqui, ele tem dono,
> histórico e status.

Se quiser gerar um achado ao vivo, crie um PR com:

```python
import subprocess
def roda(cmd):
    subprocess.call(cmd, shell=True)   # shell=True com entrada externa
```

O Bandit acusa `B602 subprocess_popen_with_shell_equals_true`.

---

## Ato 11 — Segredo bloqueado duas vezes (4 min)

O ato que torna concreta a diferença entre **prevenção** e **detecção**.

Primeiro, a prevenção. No terminal, com o pre-commit instalado:

```bash
git checkout -b demo/segredo
echo 'AWS_KEY = "AKIAIOSFODNN7EXAMPLE"' >> src/cotacao/flags.py
git commit -am "demo: credencial por engano"
```

O commit **não acontece**: o Gitleaks bloqueia antes, na máquina de quem
escreveu. Mostre a saída do hook.

Agora fure o bloqueio, como qualquer pessoa apressada faria:

```bash
git commit -am "demo: credencial por engano" --no-verify
git push -u origin demo/segredo
```

Abra o PR. O job `Segredos (Gitleaks)` fica **vermelho**.

> O ponto: o hook local é mais rápido e mais barato, mas é opcional e
> burlável. A esteira é lenta e cara, e não é nenhum dos dois. Por isso as
> duas camadas — é exatamente o que o slide 16 chama de gate de pré-commit
> e o slide 22 mostra rodando no CI.

E a pergunta que fecha o ato:

> "Removi a linha e commitei de novo. Estou seguro?"
> Não. O segredo continua no histórico do Git — por isso o `fetch-depth: 0`
> no checkout. A única resposta correta é **rotacionar a credencial**.
> Apagar o arquivo não desvaza nada.

Limpe depois: `git push origin --delete demo/segredo`.

---

## Ato 12 — O SBOM (3 min)

Dispare o **CD** e abra o log do job `Gerar artefato`, step
**Gerar SBOM (CycloneDX)**:

```
requirements.txt declara:
  requests==2.34.2
O SBOM lista:
  - certifi 2026.7.22
  - charset-normalizer 3.5.1
  - idna 3.19
  - requests 2.34.2
  - urllib3 2.7.0
```

> Uma linha declarada, cinco componentes entregues. As outras quatro ninguém
> escolheu — vieram junto — e são tão sua responsabilidade quanto o código
> que você escreveu. É o slide 17 em uma tela.

Baixe o artefato e abra o `sbom.cdx.json`. Mostre que cada componente tem um
`purl` (identificador universal do pacote).

> Amarre com o passo 3 do slide 19: quando sai uma CVE de `urllib3`, a
> pergunta "estamos afetados?" vira um `grep` neste arquivo — em segundos, e
> não em dias de busca repositório por repositório. Foi exatamente essa
> pergunta que consumiu semanas de muitos times no Log4J.

---

## Ato 13 — Uma CVE de verdade (2 min)

Mostre o commit `d440694` no histórico:

```
fix(deps): atualiza requests para 2.34.2 (PYSEC-2026-2275)
```

> Isso não foi encenado. A esteira ficou vermelha sozinha, num dia em que
> ninguém tocou no código, porque uma vulnerabilidade nova foi publicada
> para uma dependência que já estava lá. Foi o `pip-audit` no gatilho
> agendado — o callout 1 do slide 22.

Feche o arco do módulo:

> A esteira do M2 respondia "o código funciona?". Esta responde
> "o que estamos entregando é seguro?" — e responde sozinha, toda segunda,
> mesmo quando o time está de férias.

---

## Perguntas que costumam aparecer

**"Por que três workflows e não um só?"**
Objetivos diferentes mudam em ritmos diferentes e podem ter gatilhos
diferentes — repare que o de segurança também roda semanalmente por
`schedule`, porque dependências ficam vulneráveis sem ninguém tocar no código.

**"A matriz não deixa a esteira lenta?"**
Os jobs rodam em paralelo. O custo é de minutos de runner, não de tempo de
espera do time.

**"Por que os testes não acessam a API de verdade?"**
Um teste que depende de rede falha por motivos alheios ao código, e falha
intermitente destrói a confiança na esteira. Por isso o cliente HTTP é testado
com mocks. Testes contra a API real existem, mas ficam em outra etapa.

**"E se eu precisar de um segredo, como um token?"**
Vai em `Settings → Secrets and variables → Actions`, e é lido no YAML como
`${{ secrets.NOME }}`. Nunca no código — e o GitHub mascara o valor nos logs.

**"Por que o CodeQL está por tag `@v4` se a regra é fixar por SHA?"**
Porque a documentação do próprio GitHub pede a tag de major para essa action:
parte das funcionalidades depende de flags do lado do servidor, e uma versão
antiga presa por SHA vai perdendo capacidade em silêncio. A regra continua
sendo SHA por padrão; tag apenas quando quem mantém a action pede. É a única
exceção no repositório inteiro — e está comentada no arquivo.

**"Preciso pagar alguma coisa para ter isso?"**
Neste repositório, não: em repositório **público**, code scanning e secret
scanning são gratuitos. Em repositório privado é preciso GitHub Advanced
Security. O `pip-audit`, o `bandit`, o `gitleaks` e o SBOM funcionam em
qualquer caso, porque rodam como ferramentas dentro do runner.

**"Apaguei o segredo do arquivo e commitei. Resolveu?"**
Não. Ele continua no histórico do Git, e o histórico é público. Rotacione a
credencial — é a única ação que realmente resolve. Apagar o arquivo só
esconde.

**"Por que o SBOM é gerado no CD e não no CI?"**
Porque ele descreve o que foi **entregue**, não o que foi testado. Ele viaja
junto do artefato, no mesmo `upload-artifact`: se alguém perguntar daqui a
seis meses o que havia na versão publicada, a resposta está lá.
