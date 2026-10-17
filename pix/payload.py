from decimal import Decimal

from pix.crc import crc16_ccitt
from pix.emv import tlv
import unicodedata
GUI_PIX = "br.gov.bcb.pix"


def normalizar_texto(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = " ". join(texto.split())
    return texto


def formatar_valor(valor: Decimal) -> str:
    if not isinstance(valor, Decimal):
        raise TypeError ("Tipo inválido.")
    
    if valor <=0:
        raise ValueError('Valor igual a 0 ou negativo.')

    
    if Decimal(valor).as_tuple().exponent < -2:
        raise ValueError("Mais de duas casas decimais")
    
    texto = f"{Decimal(valor):.2f}"

    if len(texto) > 13:
        raise ValueError("Limite Excedido.")

    return texto



def build_static_payload(
    chave: str,
    nome: str,
    cidade: str,
    valor: Decimal | None = None,
    txid: str = "***",
    info_adicional: str | None = None,
) -> str:
    payload = ""
    chave = chave.strip()
    if not chave:
        raise ValueError("Chave Vazia!!!!")
    
    nome = normalizar_texto(nome)

    cidade = normalizar_texto(cidade)

    if not 1 <= len(nome) <= 25:
        raise ValueError("Nome deve ter de 1 a 25 caracteres")

    if not 1 <= len(cidade) <= 15:
            raise ValueError("Cidade deve ter de 1 a 15 caracteres")

    if txid != "***":
            if not 1 <= len(txid) <= 25:
                 raise ValueError('TXID deve ter entre 1 e 25 caracteres.')
            if not (txid.isascii() and txid.isalnum()):
                 raise ValueError("Os caracteres tem que ser caracteres de A-Z, a-z, 0-9")
    
    if info_adicional:
        info_adicional = normalizar_texto(info_adicional)

    conta = tlv("00", GUI_PIX) + tlv("01",chave)
    if info_adicional:
         conta += tlv("02", info_adicional)


    payload += tlv("00", "01")
    payload += tlv("26", conta)
    payload += tlv("52", "0000")
    payload += tlv("53", "986")
    if valor is not None:
         payload += tlv("54", formatar_valor(valor))
    payload += tlv("58", "BR")
    payload += tlv("59", nome)
    payload += tlv("60", cidade)
    payload += tlv("62", tlv("05", txid))
    payload += "6304"
    payload += crc16_ccitt(payload)

    return payload
