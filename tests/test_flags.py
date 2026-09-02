"""Testes das feature flags e do seu efeito na saída."""

import unittest
from unittest.mock import patch

from cotacao.flags import ativa
from cotacao.formatter import resumir

COTACAO = {"par": "USD-BRL", "compra": 5.40, "venda": 5.42, "variacao": -0.42}


class TestAtiva(unittest.TestCase):
    def test_desligada_por_padrao(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertFalse(ativa("COTACAO_MOSTRAR_COMPRA"))

    def test_valores_que_ligam(self):
        for valor in ("1", "true", "TRUE", "on", "sim"):
            with patch.dict("os.environ", {"COTACAO_MOSTRAR_COMPRA": valor}):
                self.assertTrue(ativa("COTACAO_MOSTRAR_COMPRA"), valor)

    def test_valores_que_mantem_desligada(self):
        for valor in ("0", "false", "off", ""):
            with patch.dict("os.environ", {"COTACAO_MOSTRAR_COMPRA": valor}):
                self.assertFalse(ativa("COTACAO_MOSTRAR_COMPRA"), valor)

    def test_flag_desconhecida_e_falsa(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertFalse(ativa("FLAG_QUE_NAO_EXISTE"))


class TestResumirComFlag(unittest.TestCase):
    def test_sem_flag_nao_mostra_compra(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(resumir(COTACAO), "USD-BRL: R$ 5,42 (-0,42%)")

    def test_com_flag_mostra_compra(self):
        with patch.dict("os.environ", {"COTACAO_MOSTRAR_COMPRA": "true"}):
            self.assertEqual(resumir(COTACAO), "USD-BRL: R$ 5,42 (-0,42%) | compra R$ 5,40")


if __name__ == "__main__":
    unittest.main()
