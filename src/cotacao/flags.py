"""Feature flags: separam o deploy do código da ativação da funcionalidade.

O código novo vai para produção desligado. Ligar é uma decisão de negócio,
tomada depois — sem novo deploy. É o que permite dizer que
"deploy não é release".
"""

from __future__ import annotations

import os

# Cada flag tem um valor padrão seguro: desligada.
PADROES = {
    "COTACAO_MOSTRAR_COMPRA": False,
}


def ativa(nome: str) -> bool:
    """Diz se a flag está ligada, lendo a variável de ambiente de mesmo nome.

    >>> ativa("COTACAO_MOSTRAR_COMPRA")
    False
    """
    bruto = os.environ.get(nome)
    if bruto is None:
        return PADROES.get(nome, False)
    return bruto.strip().lower() in {"1", "true", "on", "sim"}
