"""Testes das funções de formatação (não dependem de rede)."""

import unittest

from cotacao.formatter import formatar_brl, formatar_variacao, resumir


class TestFormatarBRL(unittest.TestCase):
    def test_valor_simples(self):
        self.assertEqual(formatar_brl(12.5), "R$ 12,50")

    def test_milhar(self):
        self.assertEqual(formatar_brl(1234.5), "R$ 1.234,50")

    def test_milhao(self):
        self.assertEqual(formatar_brl(1234567.89), "R$ 1.234.567,89")

    def test_arredondamento(self):
        self.assertEqual(formatar_brl(0.985), "R$ 0,98")


class TestFormatarVariacao(unittest.TestCase):
    def test_positiva_ganha_sinal(self):
        self.assertEqual(formatar_variacao(1.5), "+1,50%")

    def test_negativa_mantem_sinal(self):
        self.assertEqual(formatar_variacao(-0.42), "-0,42%")

    def test_zero_sem_sinal(self):
        self.assertEqual(formatar_variacao(0), "0,00%")


class TestResumir(unittest.TestCase):
    def test_monta_linha_legivel(self):
        cotacao = {"par": "USD-BRL", "compra": 5.0, "venda": 5.42, "variacao": -0.42}
        self.assertEqual(resumir(cotacao), "USD-BRL: R$ 5,42 (-0,42%)")


if __name__ == "__main__":
    unittest.main()
