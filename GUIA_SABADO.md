# Guia do sábado — Pix por dentro

Meta: até 12h, um gerador de Pix copia e cola funcionando na internet, com testes passando, README e rascunho do post.

## Antes de começar (5 min)

```bash
cd pix-por-dentro
uv sync                    # cria .venv e instala tudo
uv run pytest              # deve mostrar 58 failed, 2 passed
```

Sem uv: `python -m venv .venv`, ative, `pip install -r requirements.txt pytest httpx`, depois `pytest`.

Os 58 testes vermelhos são o mapa da manhã. Cada etapa deixa um arquivo de teste verde.

## A regra com a IA

Você digita ou revisa cada linha. A IA explica, dá dica e revisa. Na prática:

- Peça explicação antes de pedir código. Exemplo: *"Me explica o que o registrador do CRC faz quando o bit 0x8000 está ligado. Sem código."*
- Travou: peça a escada de dicas aqui no chat (dica 1 conceitual → dica 2 direção → dica 3 esqueleto). A solução só depois de tentar.
- Fechou uma etapa: cole o código aqui e peça revisão.
- Checkpoint de cada etapa: responder as perguntas abaixo em uma frase, sem olhar. Se não conseguir, a etapa não terminou.

## Roteiro

| Horário | Etapa | Arquivo | Testes | Pronto quando |
|---|---|---|---|---|
| 8:00–8:20 | 0. Ler a especificação | `ESPEC_BRCODE.md` | — | Você monta "5802BR" e "62070503***" de cabeça |
| 8:20–9:05 | 1. CRC16 | `pix/crc.py` | `uv run pytest tests/test_1_crc.py` | 6 verdes |
| 9:05–9:35 | 2. TLV | `pix/emv.py` | `uv run pytest tests/test_2_emv.py` | 15 verdes |
| 9:35–10:25 | 3. Payload | `pix/payload.py` | `uv run pytest tests/test_3_payload.py` | 28 verdes, incluindo o exemplo oficial do BCB |
| 10:25–10:45 | 4. API | `app/main.py` | `uv run pytest tests/test_4_api.py` | 5 verdes + página funcionando em localhost |
| 10:45–11:00 | **Teste real** | — | — | O app do seu banco lê o seu QR e mostra seu nome |
| 11:00–11:20 | Deploy + GitHub | `render.yaml` | — | Link público abrindo |
| 11:20–11:40 | README + prints | `README.md` | — | README completo |
| 11:40–12:00 | Post | — | — | Rascunho pronto para revisar |
| Se sobrar tempo | 5. Decodificador (bônus) | `pix/decoder.py` | `uv run pytest tests/test_5_decoder.py` | 6 verdes |

Corte de escopo se atrasar: o decodificador sai primeiro. O deploy pode ir para domingo; o post sai com print local. O que **não** sai: testes verdes e o teste real no app do banco.

## Checkpoints (responda sem olhar)

**Etapa 1 — CRC**
1. Por que a entrada do cálculo inclui "6304"?
2. O que dá errado se você esquecer do `& 0xFFFF`?
3. Para que serve um CRC? Ele protege contra fraude?

**Etapa 2 — TLV**
1. Por que o valor de um campo não pode passar de 99 caracteres?
2. Como o leitor sabe onde um campo termina, se não existe separador?

**Etapa 3 — Payload**
1. Por que `formatar_valor` recusa `float`? Mostre `0.1 + 0.2` no terminal.
2. Por que remover acentos? (pense em caractere × byte)
3. Por que "Angical do Piauí" é recusado, e por que recusar é melhor que truncar?

**Etapa 4 — API**
1. Qual a diferença entre o 422 que o Pydantic gera e o 422 que você gera?
2. O que o `raise ... from erro` preserva?

## Teste real (o momento do post)

1. Rode `uv run uvicorn app.main:app --reload` e abra `http://127.0.0.1:8000`.
2. Gere um QR com **a sua chave Pix**, seu nome e um valor baixo (R$ 0,01 ou R$ 1,00).
3. No app do banco, escolha pagar com QR Code e leia a tela.
4. Confira: o app mostra o **seu nome como cadastrado no banco** (vem do DICT, não do campo 59) e o valor.
5. Pague R$ 0,01 para você mesmo se quiser a prova completa. Tire print (borre dados sensíveis).

Se o app recusar: rode os testes de novo. O suspeito número 1 é o CRC; o número 2 é tamanho de campo.

## Deploy no Render (gratuito)

1. Crie o repositório `pix-por-dentro` no GitHub e faça push.
2. Em render.com: New → Blueprint → aponte para o repositório. O `render.yaml` já tem tudo.
3. Primeiro acesso depois de um tempo parado demora (o plano gratuito hiberna). Avise isso no README.

## Prints para o post

- Os testes verdes no terminal, com destaque para `test_reproduz_exemplo_oficial_do_banco_central`.
- A seção "Anatomia" da página, mostrando os campos.
- A tela do app do banco lendo o seu QR (dados sensíveis borrados).
- O trecho do `crc16_ccitt` (é curto e chama atenção).

`docs/como-deve-ficar.png` mostra o resultado final esperado da página.

## Post

Quando terminar, volte aqui com: o que deu errado de verdade (todo projeto tem um), o print e o link. O rascunho sai com a skill `li-post`, no tipo "bug ou erro que ensinou" ou "conceito com código". Só entra no post o que você consegue explicar.
