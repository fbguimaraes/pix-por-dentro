import pytest

from pix.emv import parse_tlv, tlv


def test_campo_simples():
    assert tlv("58", "BR") == "5802BR"


def test_tamanho_com_zero_a_esquerda():
    assert tlv("53", "986") == "5303986"
    assert tlv("05", "***") == "0503***"


def test_campo_aninhado():
    interno = tlv("00", "br.gov.bcb.pix") + tlv("01", "abc")
    assert tlv("26", interno) == "26250014br.gov.bcb.pix0103abc"


def test_tamanho_maximo_99():
    assert tlv("26", "x" * 99).startswith("2699")
    with pytest.raises(ValueError):
        tlv("26", "x" * 100)


@pytest.mark.parametrize("id_invalido", ["5", "123", "AB", ""])
def test_id_precisa_de_dois_digitos(id_invalido):
    with pytest.raises(ValueError):
        tlv(id_invalido, "BR")


def test_valor_vazio_e_invalido():
    with pytest.raises(ValueError):
        tlv("59", "")


def test_parse_nivel_raiz():
    assert parse_tlv("5802BR5913Fulano de Tal") == [("58", "BR"), ("59", "Fulano de Tal")]


def test_parse_nao_desce_no_aninhado():
    campos = parse_tlv("26250014br.gov.bcb.pix0103abc5802BR")
    assert campos == [("26", "0014br.gov.bcb.pix0103abc"), ("58", "BR")]


def test_ida_e_volta():
    original = [("00", "01"), ("53", "986"), ("59", "Ana")]
    texto = "".join(tlv(i, v) for i, v in original)
    assert parse_tlv(texto) == original


@pytest.mark.parametrize("truncado", ["58", "5802B", "5810BR"])
def test_parse_truncado_levanta_erro(truncado):
    with pytest.raises(ValueError):
        parse_tlv(truncado)
