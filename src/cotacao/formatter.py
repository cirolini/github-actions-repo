"""Formatação de valores monetários e variações percentuais."""

from __future__ import annotations

from cotacao.flags import ativa


def formatar_brl(valor: float) -> str:
    """Formata um número no padrão monetário brasileiro.

    >>> formatar_brl(1234.5)
    'R$ 1.234,50'
    """
    inteiro, decimal = f"{valor:.2f}".split(".")
    grupos = []
    while len(inteiro) > 3:
        grupos.insert(0, inteiro[-3:])
        inteiro = inteiro[:-3]
    grupos.insert(0, inteiro)
    return f"R$ {'.'.join(grupos)},{decimal}"


def formatar_variacao(pct: float) -> str:
    """Formata a variação percentual com sinal explícito.

    >>> formatar_variacao(-0.42)
    '-0,42%'
    """
    sinal = "+" if pct > 0 else ""
    return f"{sinal}{pct:.2f}".replace(".", ",") + "%"


def resumir(cotacao: dict) -> str:
    """Monta uma linha legível a partir do dicionário de cotação.

    Quando a flag COTACAO_MOSTRAR_COMPRA está ligada, inclui também o
    preço de compra. O código vai para produção com a flag desligada.
    """
    linha = (
        f"{cotacao['par']}: {formatar_brl(cotacao['venda'])} "
        f"({formatar_variacao(cotacao['variacao'])})"
    )
    if ativa("COTACAO_MOSTRAR_COMPRA"):
        linha += f" | compra {formatar_brl(cotacao['compra'])}"
    return linha
