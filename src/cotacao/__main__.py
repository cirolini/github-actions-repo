"""Ponto de entrada da CLI: python -m cotacao USD-BRL."""

from __future__ import annotations

import sys

from cotacao.client import CotacaoError, buscar_cotacao
from cotacao.formatter import resumir


def main(argv: list[str] | None = None) -> int:
    argumentos = argv if argv is not None else sys.argv[1:]
    par = argumentos[0] if argumentos else "USD-BRL"

    try:
        cotacao = buscar_cotacao(par)
    except CotacaoError as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 1

    print(resumir(cotacao))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
