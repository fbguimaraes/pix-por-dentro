"""Bônus. Rode com: pytest tests/test_5_decoder.py"""

from decimal import Decimal

import pytest

from pix.decoder import decodificar
from tests.vetores_oficiais import BRCODE_MULTI, CHAVE_ALEATORIA, DINAMICO, ESTATICO

pytestmark = pytest.mark.skip(reason="decodificador: próximo passo do projeto")

def test_decodifica_estatico():
    dados = decodificar(ESTATICO)
    assert dados["chave"] == CHAVE_ALEATORIA
    assert dados["nome"] == "Fulano de Tal"
    assert dados["cidade"] == "BRASILIA"
    assert dados["valor"] is None
    assert dados["txid"] == "***"
    assert dados["url"] is None
    assert dados["uso_unico"] is False


def test_decodifica_dinamico_com_url():
    dados = decodificar(DINAMICO)
    assert dados["chave"] is None
    assert dados["url"] == "pix.example.com/8b3da2f39a4140d1a91abd93113bd441"
    assert dados["uso_unico"] is True


def test_acha_o_pix_no_meio_de_outros_arranjos():
    dados = decodificar(BRCODE_MULTI)
    assert dados["chave"] == CHAVE_ALEATORIA
    assert dados["valor"] == Decimal("123.45")
    assert dados["txid"] == "RP12345678-2019"


def test_aceita_espacos_e_quebra_de_linha_nas_pontas():
    assert decodificar(f"  {ESTATICO}\n")["nome"] == "Fulano de Tal"


def test_crc_adulterado():
    adulterado = ESTATICO.replace("Fulano", "Fulana")
    with pytest.raises(ValueError, match="CRC"):
        decodificar(adulterado)


def test_texto_qualquer():
    with pytest.raises(ValueError):
        decodificar("isto não é um pix")
