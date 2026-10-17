from fastapi.testclient import TestClient

from app.main import app
from tests.vetores_oficiais import CHAVE_ALEATORIA, ESTATICO

client = TestClient(app)


def test_health():
    resposta = client.get("/health")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_pagina_inicial():
    resposta = client.get("/")
    assert resposta.status_code == 200
    assert "text/html" in resposta.headers["content-type"]


def test_gera_pix_igual_ao_manual():
    resposta = client.post(
        "/api/pix",
        json={"chave": CHAVE_ALEATORIA, "nome": "Fulano de Tal", "cidade": "BRASILIA"},
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["payload"] == ESTATICO
    assert corpo["qr_svg"].startswith("<svg")


def test_valor_vai_como_texto_e_vira_decimal():
    resposta = client.post(
        "/api/pix",
        json={"chave": CHAVE_ALEATORIA, "nome": "Fulano", "cidade": "Teresina", "valor": "12.50"},
    )
    assert resposta.status_code == 200
    assert "540512.50" in resposta.json()["payload"]


def test_erro_de_regra_vira_422_com_mensagem():
    resposta = client.post(
        "/api/pix",
        json={"chave": CHAVE_ALEATORIA, "nome": "Fulano", "cidade": "Angical do Piauí"},
    )
    assert resposta.status_code == 422
    assert "detail" in resposta.json()
