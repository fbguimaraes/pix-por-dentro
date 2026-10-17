# O que tem dentro de um Pix copia e cola

 Tudo aqui vem dos dois manuais do Banco Central listados em "Fontes".

## 1. O problema

O QR Code do Pix é só uma imagem de um texto. Esse texto é o mesmo que você cola no "Pix copia e cola". O Banco Central não inventou um formato: adotou o padrão internacional **EMV QRCPS – Merchant Presented Mode** (o comerciante mostra o QR, o cliente lê) e chamou a versão brasileira de **BR Code**.

Por isso o texto parece sopa de números. Ele é uma sequência de campos, sem separador.

## 2. O formato: TLV

Cada campo tem três partes coladas:

```
ID (2 dígitos) + TAMANHO (2 dígitos) + VALOR (TAMANHO caracteres)
```

| Campo | Escrito | Lendo |
|---|---|---|
| País = "BR" | `5802BR` | ID 58, tamanho 02, valor `BR` |
| Moeda = real | `5303986` | ID 53, tamanho 03, valor `986` (ISO 4217) |
| Nome | `5913Fulano de Tal` | ID 59, tamanho 13, valor `Fulano de Tal` |

O leitor sabe onde cada campo termina porque o tamanho vem antes. Dois dígitos de tamanho significam **no máximo 99 caracteres** por campo.

Alguns campos guardam outros campos dentro (templates). O 26 é o principal:

```
26 58                                       ← campo 26, 58 caracteres de conteúdo
   00 14 br.gov.bcb.pix                     ← GUI: "este bloco é do Pix"
   01 36 123e4567-e12b-12d1-a456-426655440000   ← a chave Pix
```

4 + 14 + 4 + 36 = 58. Confira.

## 3. Os campos do Pix estático

Ordem usada no exemplo oficial (Manual de Padrões para Iniciação do Pix, seção 2.6.3):

| ID | Nome EMV | Obrigatório | Valor no Pix | Limite |
|---|---|---|---|---|
| 00 | Payload Format Indicator | sim | `01` | fixo |
| 01 | Point of Initiation Method | não | `12` = uso único | — |
| 26 | Merchant Account Information | sim | ver abaixo | até 99 |
| 52 | Merchant Category Code | sim | `0000` | 4 |
| 53 | Transaction Currency | sim | `986` | 3 |
| 54 | Transaction Amount | não | ex.: `25.90` | 1 a 13 |
| 58 | Country Code | sim | `BR` | 2 |
| 59 | Merchant Name | sim | nome | 1 a 25 |
| 60 | Merchant City | sim | cidade | 1 a 15 |
| 62 | Additional Data Field | sim | subcampo 05 = txid | — |
| 63 | CRC16 | sim | 4 dígitos hex | 4 |

Dentro do 26:

| Sub-ID | Nome | Regra |
|---|---|---|
| 00 | GUI | `br.gov.bcb.pix` (maiúsculas ou minúsculas tanto faz) |
| 01 | chave | até 77 caracteres quando não há 02 |
| 02 | infoAdicional | texto livre que aparece para quem paga |
| 25 | URL | só no Pix **dinâmico** (no lugar da chave) |

Chave, infoAdicional e o resto do 26 disputam os mesmos 99 caracteres. Chave grande deixa menos espaço para mensagem.

### Formato das chaves

| Tipo | Como escrever |
|---|---|
| E-mail | `fulano@example.com` |
| CPF / CNPJ | só dígitos: `12345678900` |
| Celular | formato internacional: `+5586912345678` |
| Aleatória | com hífens: `123e4567-e12b-12d1-a456-426655440000` |

### txid (campo 62, subcampo 05)

- Até 25 caracteres, só `A-Z`, `a-z` e `0-9` no Pix estático.
- Sem txid, o valor é `***` (três asteriscos). O manual explica que isso vem do padrão EMV: `***` significa "o app de quem paga se vira".

### Nome que aparece para quem paga

O app do banco mostra o nome **cadastrado no DICT** para aquela chave, não o campo 59. Por isso o teste real é tão convincente: se o QR estiver certo, aparece o seu nome de verdade.

## 4. O CRC16 (campo 63)

Um código de verificação de 16 bits sobre todo o resto do texto. Se um caractere mudar, o CRC muda e o app recusa.

Parâmetros: polinômio `0x1021`, valor inicial `0xFFFF`. Essa combinação, sem reflexão de bits e sem XOR final, é a variante **CRC-16/CCITT-FALSE**.

A armadilha: a entrada do cálculo é **tudo até o "6304" inclusive**. Você escreve `...6304`, calcula o CRC desse texto e cola os 4 dígitos no final.

| Entrada | Resultado no exemplo oficial |
|---|---|
| Texto terminando em `6304` | `1D3D` ✅ |
| Texto sem o `6304` | outro valor ❌ |

Com o CRC errado, qualquer leitor de QR decodifica o texto normalmente. Só o banco recusa. Por isso o teste `test_armadilha_sem_o_6304_da_outro_valor` existe.

Para conferir os parâmetros antes de tudo: o CRC-16/CCITT-FALSE de `"123456789"` é `29B1`.

**O CRC não é segurança.** Qualquer um recalcula. Ele pega erro acidental, não fraude.

## 5. O exemplo oficial, campo a campo

```
00 02 01
26 58
   00 14 br.gov.bcb.pix
   01 36 123e4567-e12b-12d1-a456-426655440000
52 04 0000
53 03 986
58 02 BR
59 13 Fulano de Tal
60 08 BRASILIA
62 07
   05 03 ***
63 04 1D3D
```

Tudo junto:

```
00020126580014br.gov.bcb.pix0136123e4567-e12b-12d1-a456-4266554400005204000053039865802BR5913Fulano de Tal6008BRASILIA62070503***63041D3D
```

O teste `test_reproduz_exemplo_oficial_do_banco_central` exige que o seu código gere exatamente isso.

## 6. Decisões do projeto (que valem um parágrafo no README)

| Decisão | Por quê |
|---|---|
| Remover acentos de nome, cidade e mensagem | O tamanho TLV conta caracteres; "ã" ocupa 2 bytes em UTF-8. ASCII elimina a ambiguidade |
| Recusar em vez de truncar | Truncar "Angical do Piauí" para "Angical do Piau" esconde o problema do usuário |
| `Decimal`, nunca `float`, para valor | `0.1 + 0.2 != 0.3` em float. Dinheiro não pode depender disso |
| Recusar mais de 2 casas decimais | Arredondar dinheiro em silêncio é bug esperando acontecer |
| Testes com os exemplos dos manuais | A prova de corretude é externa ao código |

## 7. Estático × dinâmico (para responder nos comentários)

| | Estático (este projeto) | Dinâmico |
|---|---|---|
| Dados | todos dentro do QR | o QR guarda uma URL; os dados vêm de lá |
| Quem gera | qualquer software | só via API Pix do PSP (banco) |
| Conciliação | txid opcional, sem garantia de unicidade | txid de 26 a 35 caracteres, único |
| Uso típico | QR fixo no balcão, cobrança simples | e-commerce, cobrança com vencimento |

## Fontes

- **Manual do BR Code**, Banco Central, v2.0.1 — seção 2.1 (tabela 1 com todos os campos e a nota 10 sobre o CRC) e seção 2.2 (exemplo com vários arranjos, CRC `AD38`).
  https://www.bcb.gov.br/content/estabilidadefinanceira/spb_docs/ManualBRCode.pdf
- **Manual de Padrões para Iniciação do Pix**, Banco Central — seções 2.5.1 (formato das chaves), 2.6 a 2.6.3 (QR estático, txid e o exemplo `1D3D`) e 2.7.2 (exemplo dinâmico `64E4`).
  https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Regulamento_Pix/II_ManualdePadroesparaIniciacaodoPix.pdf

### Inglês técnico (5 min)

O manual do Pix cita a especificação EMV, seção 4.8.1.2, em inglês. Leia no Manual de Padrões a nota de rodapé 25 (a frase sobre `"***"`).

Pergunta: segundo esse trecho, quem fica responsável por obter a informação quando o valor é `***`?

Glossário que entra hoje: *payload*, *checksum*, *merchant*, *template*, *reference label*, *point of initiation*.
