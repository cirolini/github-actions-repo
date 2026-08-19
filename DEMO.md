# Roteiro de demonstração em aula

Sequência para mostrar a esteira funcionando, falhando e sendo corrigida.
Tempo total: 12 a 15 minutos. Casa com a Seção 4 do Módulo 2 (slides 20 a 24).

---

## Antes da aula

1. Faça o push inicial e confirme que a aba **Actions** está verde.
2. Ligue a proteção da branch (`Settings → Branches`), exigindo o job
   `Lint e testes` — sem isso a demonstração do bloqueio não funciona.
3. Deixe duas abas abertas: o repositório e a aba Actions.

---

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

## Ato 5 — Entrega contínua (2 min, opcional)

Na aba Actions, dispare o **CD** manualmente (`Run workflow`).

Mostre que:

- o job `empacotar` roda sozinho e gera o artefato;
- o job `publicar` fica **aguardando aprovação**;
- o artefato pode ser baixado da própria execução.

> Aqui fica visível a diferença entre entrega e implantação contínua: a esteira
> deixou tudo pronto, mas quem decide publicar é uma pessoa. Tirar essa
> aprovação transforma entrega contínua em implantação contínua.

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
