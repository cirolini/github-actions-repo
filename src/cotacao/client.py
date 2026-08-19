"""Cliente HTTP para a API pública de cotações da AwesomeAPI."""

from __future__ import annotations

import requests

BASE_URL = "https://economia.awesomeapi.com.br/json/last"
TIMEOUT_SEGUNDOS = 10


class CotacaoError(RuntimeError):
    """Falha ao consultar ou interpretar a cotação."""


def buscar_cotacao(par: str = "USD-BRL", session: requests.Session | None = None) -> dict:
    """Busca a cotação mais recente de um par de moedas.

    Args:
        par: par no formato "USD-BRL".
        session: sessão HTTP opcional, útil para testes.

    Returns:
        Dicionário com as chaves ``par``, ``compra``, ``venda`` e ``variacao``.

    Raises:
        CotacaoError: se a API responder com erro ou payload inesperado.
    """
    http = session or requests
    url = f"{BASE_URL}/{par}"

    try:
        resposta = http.get(url, timeout=TIMEOUT_SEGUNDOS)
        resposta.raise_for_status()
        dados = resposta.json()
    except requests.RequestException as erro:
        raise CotacaoError(f"Falha de rede ao consultar {par}: {erro}") from erro
    except ValueError as erro:
        raise CotacaoError(f"Resposta da API não é um JSON válido: {erro}") from erro

    chave = par.replace("-", "")
    if chave not in dados:
        raise CotacaoError(f"Par {par} não encontrado na resposta da API")

    bruto = dados[chave]
    return {
        "par": par,
        "compra": float(bruto["bid"]),
        "venda": float(bruto["ask"]),
        "variacao": float(bruto["pctChange"]),
    }
