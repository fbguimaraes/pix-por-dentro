from decimal import Decimal

import pytest

from pix.crc import crc16_ccitt
from pix.payload import build_static_payload, formatar_valor, normalizar_texto
from tests.vetores_oficiais import CHAVE_ALEATORIA, ESTATICO

# --- normalizar_texto -------------------------------------------------------


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("São Paulo", "Sao Paulo"),
        ("  Fabrício   Guimarães ", "Fabricio Guimaraes"),
        ("Café da manhã", "Cafe da manha"),
        ("BRASILIA", "BRASILIA"),
    ],
)
def test_normalizar_texto(entrada, esperado):
    assert normalizar_texto(entrada) == esperado


# --- formatar_valor ---------------------------------------------------------


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        (Decimal("10"), "10.00"),
        (Decimal("25.9"), "25.90"),
        (Decimal("0.01"), "0.01"),
        (Decimal("9999999999.99"), "9999999999.99"),
    ],
)
def test_formatar_valor(valor, esperado):
    assert formatar_valor(valor) == esperado


def test_float_e_recusado():
    with pytest.raises(TypeError):
        formatar_valor(10.5)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "valor",
    [Decimal("0"), Decimal("-5"), Decimal("12.345"), Decimal("10000000000.00")],
)
def test_valores_invalidos(valor):
    with pytest.raises(ValueError):
        formatar_valor(valor)


# --- build_static_payload ---------------------------------------------------


def test_reproduz_exemplo_oficial_do_banco_central():
    assert build_static_payload(CHAVE_ALEATORIA, "Fulano de Tal", "BRASILIA") == ESTATICO


def test_com_valor_email_txid_e_info_adicional():
    payload = build_static_payload(
        chave="fabricio@example.com",
        nome="Fabrício Guimarães",
        cidade="Angical do PI",
        valor=Decimal("25.90"),
        txid="CAFE01",
        info_adicional="Café da manhã",
    )
    assert payload == (
        "00020126590014br.gov.bcb.pix0120fabricio@example.com0213Cafe da manha"
        "520400005303986540525.905802BR5918Fabricio Guimaraes6013Angical do PI"
        "62100506CAFE0163040809"
    )


def test_telefone_e_valor_inteiro():
    payload = build_static_payload("+5586999999999", "Loja Exemplo", "Teresina", Decimal("10"))
    assert payload == (
        "00020126360014br.gov.bcb.pix0114+5586999999999520400005303986540510.00"
        "5802BR5912Loja Exemplo6008Teresina62070503***63045768"
    )


def test_cpf_com_info_adicional_sem_valor():
    payload = build_static_payload("12345678900", "Ana", "São Paulo", info_adicional="Mensalidade outubro")
    assert payload == (
        "00020126560014br.gov.bcb.pix0111123456789000219Mensalidade outubro"
        "5204000053039865802BR5903Ana6009Sao Paulo62070503***630478E5"
    )


def test_crc_do_proprio_payload_confere():
    payload = build_static_payload(CHAVE_ALEATORIA, "Teste", "Teresina", Decimal("1.50"))
    assert payload[-8:-4] == "6304"
    assert crc16_ccitt(payload[:-4]) == payload[-4:]


def test_sem_valor_nao_tem_campo_54():
    payload = build_static_payload(CHAVE_ALEATORIA, "Fulano de Tal", "BRASILIA")
    assert "5303986" + "5802BR" in payload


def test_cidade_com_16_caracteres_e_recusada():
    # "Angical do Piaui" tem 16 caracteres: o limite do campo 60 é 15.
    with pytest.raises(ValueError):
        build_static_payload(CHAVE_ALEATORIA, "Fulano", "Angical do Piauí")


def test_nome_com_26_caracteres_e_recusado():
    with pytest.raises(ValueError):
        build_static_payload(CHAVE_ALEATORIA, "A" * 26, "Teresina")


@pytest.mark.parametrize("chave", ["", "   "])
def test_chave_vazia(chave):
    with pytest.raises(ValueError):
        build_static_payload(chave, "Fulano", "Teresina")


@pytest.mark.parametrize("txid", ["com-hifen", "A" * 26, "espaço aqui", ""])
def test_txid_invalido(txid):
    with pytest.raises(ValueError):
        build_static_payload(CHAVE_ALEATORIA, "Fulano", "Teresina", txid=txid)


def test_campo_26_estourando_99_caracteres():
    with pytest.raises(ValueError):
        build_static_payload(CHAVE_ALEATORIA, "Fulano", "Teresina", info_adicional="x" * 60)
