"""Testes do cliente HTTP usando mocks — a esteira nunca acessa a rede."""

import unittest
from unittest.mock import Mock

import requests

from cotacao.client import CotacaoError, buscar_cotacao

PAYLOAD_OK = {
    "USDBRL": {
        "code": "USD",
        "codein": "BRL",
        "bid": "5.4012",
        "ask": "5.4231",
        "pctChange": "-0.42",
    }
}


def _sessao_falsa(payload=None, erro=None, json_invalido=False):
    resposta = Mock()
    if json_invalido:
        resposta.json.side_effect = ValueError("Expecting value")
    else:
        resposta.json.return_value = payload
    resposta.raise_for_status.return_value = None

    sessao = Mock()
    if erro is not None:
        sessao.get.side_effect = erro
    else:
        sessao.get.return_value = resposta
    return sessao


class TestBuscarCotacao(unittest.TestCase):
    def test_retorna_campos_convertidos(self):
        resultado = buscar_cotacao("USD-BRL", session=_sessao_falsa(PAYLOAD_OK))

        self.assertEqual(resultado["par"], "USD-BRL")
        self.assertAlmostEqual(resultado["compra"], 5.4012)
        self.assertAlmostEqual(resultado["venda"], 5.4231)
        self.assertAlmostEqual(resultado["variacao"], -0.42)

    def test_monta_url_com_o_par(self):
        payload_eur = {"EURBRL": {"bid": "6.10", "ask": "6.15", "pctChange": "0.30"}}
        sessao = _sessao_falsa(payload_eur)
        buscar_cotacao("EUR-BRL", session=sessao)

        url_chamada = sessao.get.call_args[0][0]
        self.assertTrue(url_chamada.endswith("/EUR-BRL"))

    def test_envia_timeout(self):
        sessao = _sessao_falsa(PAYLOAD_OK)
        buscar_cotacao("USD-BRL", session=sessao)

        self.assertEqual(sessao.get.call_args[1]["timeout"], 10)

    def test_par_ausente_gera_erro(self):
        with self.assertRaises(CotacaoError) as ctx:
            buscar_cotacao("XXX-BRL", session=_sessao_falsa(PAYLOAD_OK))

        self.assertIn("não encontrado", str(ctx.exception))

    def test_falha_de_rede_gera_erro(self):
        sessao = _sessao_falsa(erro=requests.ConnectionError("sem rede"))

        with self.assertRaises(CotacaoError) as ctx:
            buscar_cotacao("USD-BRL", session=sessao)

        self.assertIn("Falha de rede", str(ctx.exception))

    def test_json_invalido_gera_erro(self):
        with self.assertRaises(CotacaoError) as ctx:
            buscar_cotacao("USD-BRL", session=_sessao_falsa(json_invalido=True))

        self.assertIn("JSON", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
