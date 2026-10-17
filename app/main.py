from decimal import Decimal
from pathlib import Path

import segno
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from pix.payload import build_static_payload

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Pix por dentro", version="0.1.0")


class PixEntrada(BaseModel):
    chave: str = Field(min_length=1, max_length=77)
    nome: str = Field(min_length=1, max_length=60)
    cidade: str = Field(min_length=1, max_length=60)
    valor: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    txid: str = "***"
    info_adicional: str | None = Field(default=None, max_length=72)


class PixSaida(BaseModel):
    payload: str
    qr_svg: str


def gerar_svg(payload: str) -> str:
    return segno.make_qr(payload, error="m").svg_inline(scale=6, border=2)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def pagina() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/pix", response_model=PixSaida)
def gerar_pix(entrada: PixEntrada) -> PixSaida:
    try:
        payload = build_static_payload(entrada.chave, entrada.nome, entrada.cidade, entrada.valor, entrada.txid, entrada.info_adicional)
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro

    return PixSaida(payload=payload, qr_svg=gerar_svg(payload)) 


class DecodificarEntrada(BaseModel):
    payload: str = Field(min_length=8, max_length=512)


@app.post("/api/decodificar")
def decodificar_pix(entrada: DecodificarEntrada) -> dict:
    raise HTTPException(status_code=501, detail="Bônus: decodificador ainda não implementado")
