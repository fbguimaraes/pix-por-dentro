# Pix por dentro

Gerador de Pix copia e cola (BR Code estático) escrito do zero em Python, sem biblioteca de Pix, seguindo os manuais do Banco Central.

![Página do gerador](docs/como-deve-ficar.png)

## Por que fiz

Paguei um Pix, olhei para o copia e cola e resolvi entender o que era aquela sequência de números. Este projeto é a resposta: ele monta o texto campo a campo, calcula o código de verificação e gera o QR Code.

## O que tem dentro de um Pix copia e cola

O Pix usa o padrão **BR Code**, a versão brasileira do padrão internacional EMV para QR Codes de pagamento. O texto é uma sequência de campos no formato **TLV**: ID (2 dígitos) + tamanho (2 dígitos) + valor. Não existe separador: o leitor sabe onde cada campo termina porque o tamanho vem antes do valor.

O exemplo oficial do Banco Central, campo a campo:

```
00 02 01                                       versão do formato
26 58                                          conta do recebedor
   00 14 br.gov.bcb.pix                           identifica o arranjo Pix
   01 36 123e4567-e12b-12d1-a456-426655440000     chave Pix
52 04 0000                                     categoria do comerciante
53 03 986                                      moeda (real, ISO 4217)
58 02 BR                                       país
59 13 Fulano de Tal                            nome do recebedor
60 08 BRASILIA                                 cidade
62 07                                          dados adicionais
   05 03 ***                                      txid (*** = não usado)
63 04 1D3D                                     CRC16
```

Tudo junto:

```
00020126580014br.gov.bcb.pix0136123e4567-e12b-12d1-a456-4266554400005204000053039865802BR5913Fulano de Tal6008BRASILIA62070503***63041D3D
```

### O CRC16 (campo 63)

Os 4 últimos caracteres são um **CRC-16/CCITT-FALSE** (polinômio `0x1021`, valor inicial `0xFFFF`), calculado sobre todo o texto anterior, **incluindo o `6304`** (ID e tamanho do próprio campo 63).

O motivo é de convenção: a especificação EMV define assim, e quem gera o QR e quem confere (o banco) precisam calcular sobre exatamente o mesmo texto. O banco separa os 4 últimos caracteres, recalcula o CRC do resto e compara. Se um caractere mudar, o CRC muda e o pagamento é recusado.

O CRC detecta erro de digitação ou de leitura. Ele **não** é segurança contra fraude: qualquer pessoa consegue recalcular.

## O que aprendi errando

1. **Meu primeiro CRC passou no teste por coincidência.** O registrador do cálculo voltava ao valor inicial a cada byte, em vez de carregar o resultado do byte anterior. Com uma entrada de um caractere, o erro não aparece. Com dois, quebra.
2. **`not a and not b` não é o mesmo que `not (a and b)`.** Na validação do txid, a primeira forma só recusava o valor quando as duas regras falhavam ao mesmo tempo, e deixava passar um txid com hífen. A forma certa recusa quando qualquer regra falha (lei de De Morgan).

## Decisões

| Decisão | Motivo |
|---|---|
| Valor só como `Decimal`, nunca `float` | `float` não representa valores como 0,1 com exatidão (`0.1 + 0.2 != 0.3`) |
| Recusa mais de 2 casas decimais | Arredondar dinheiro em silêncio esconde erro |
| Remove acentos de nome, cidade e mensagem | O tamanho TLV conta caracteres, e "ã" ocupa 2 bytes em UTF-8 |
| Recusa em vez de truncar | Nome acima de 25 ou cidade acima de 15 caracteres vira erro claro, não um texto cortado |
| txid só com letras e números ASCII | `isalnum()` sozinho aceita "é" e dígitos de outros alfabetos, que o Pix não aceita |
| Testes com os exemplos oficiais | A prova de que o código está certo vem de fora do código |

## Como rodar

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt pytest httpx
pytest
uvicorn app.main:app --reload
```

Linux ou macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt pytest httpx
pytest
uvicorn app.main:app --reload
```

Depois, abra http://127.0.0.1:8000.

## API

`POST /api/pix`

```json
{
  "chave": "fulano@example.com",
  "nome": "Fulano de Tal",
  "cidade": "Teresina",
  "valor": "10.00",
  "txid": "PEDIDO1"
}
```

Resposta:

```json
{
  "payload": "000201...",
  "qr_svg": "<svg ...>"
}
```

Os campos `valor`, `txid` e `info_adicional` são opcionais. O valor vai como texto (`"10.00"`) para chegar ao servidor como `Decimal`, sem passar por `float`. Erros de regra voltam como **422**, com a mensagem explicando o que corrigir.

## Testes

São 54 testes. O principal reproduz, caractere por caractere, o exemplo oficial do *Manual de Padrões para Iniciação do Pix* (CRC `1D3D`). O CRC também é conferido contra os exemplos `64E4` (Pix dinâmico) e `AD38` (Manual do BR Code), e contra o vetor canônico da variante (`"123456789"` → `29B1`).

Além dos testes, o QR gerado foi lido no app de um banco, que reconheceu a chave e mostrou o nome do recebedor.

## Estrutura

```
pix/crc.py         CRC-16/CCITT-FALSE
pix/emv.py         TLV: montar e ler campos
pix/payload.py     regras do Pix estático e montagem do payload
pix/decoder.py     leitura de um Pix copia e cola (próximo passo)
app/main.py        API FastAPI e página
app/static/        página com o QR e a "anatomia" dos campos
tests/             pytest com os exemplos oficiais do Banco Central
ESPEC_BRCODE.md    a especificação explicada
```

## Como foi feito

Usei IA (Claude, da Anthropic) como mentora. Ela preparou um kit de estudo com esqueletos e testes, explicou os conceitos quando eu travava e revisou o meu código a cada etapa. **A implementação foi escrita por mim.** Os erros descritos acima também foram meus.

Antes de publicar, pedi à IA apenas para remover os comentários de exercício do código. A publicação foi feita por mim.

O kit de estudo, sem as soluções, para quem quiser fazer o mesmo caminho: [\[link do repositório do kit\]](https://github.com/fbguimaraes/kit-pix-por-dentro.git)

## Limites

- Só Pix **estático**. O dinâmico exige a API Pix de um banco (PSP).
- Projeto de estudo. Confira nome e valor no app do banco antes de pagar.

## Próximos passos

- Decodificador: colar um Pix copia e cola e ver os campos.
- Deploy.

## Fontes

- [Manual do BR Code — Banco Central](https://www.bcb.gov.br/content/estabilidadefinanceira/spb_docs/ManualBRCode.pdf), seções 2.1 e 2.2.
- [Manual de Padrões para Iniciação do Pix — Banco Central](https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Regulamento_Pix/II_ManualdePadroesparaIniciacaodoPix.pdf), seções 2.5.1 e 2.6.

## Licença

MIT