import pytest

from pix.crc import crc16_ccitt
from tests.vetores_oficiais import BRCODE_MULTI, DINAMICO, ESTATICO


def test_vetor_canonico_da_variante():
    # Se este falhar, o problema está nos parâmetros (polinômio, valor inicial, reflexão).
    assert crc16_ccitt("123456789") == "29B1"


def test_sempre_quatro_digitos_maiusculos():
    resultado = crc16_ccitt("")
    assert resultado == "FFFF"
    assert len(crc16_ccitt("a")) == 4
    assert crc16_ccitt("a") == crc16_ccitt("a").upper()


@pytest.mark.parametrize(
    ("payload", "crc_esperado"),
    [(ESTATICO, "1D3D"), (DINAMICO, "64E4"), (BRCODE_MULTI, "AD38")],
)
def test_exemplos_dos_manuais_incluindo_6304_na_entrada(payload, crc_esperado):
    entrada = payload[:-4]  # termina em "6304"
    assert entrada.endswith("6304")
    assert crc16_ccitt(entrada) == crc_esperado


def test_armadilha_sem_o_6304_da_outro_valor():
    # Cortar o campo 63 inteiro é o erro mais comum: o QR lê, mas o banco recusa.
    assert crc16_ccitt(ESTATICO[:-8]) != "1D3D"
