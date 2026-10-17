def tlv(id_: str, valor: str) -> str:
    if len(id_) != 2:
        raise ValueError('tamanho Inválido de id')
    if  not id_.isdigit():
        raise ValueError('Id precisa ser número!')
    tamanho = len(str(valor))
    if not 1 <= tamanho <= 99:
        raise ValueError("Tamanho Inválido de valor!")
    return f"{id_}{tamanho:02d}{valor}"


def parse_tlv(payload: str) -> list[tuple[str, str]]:
    campos = []
    i = 0
    while i < len(payload):
        
        id_ = payload[i:i+2]
        tamanho = int(payload[i+2:i+4])
        if i + 4 + tamanho > len(payload):
            raise ValueError(f"campo {id_} truncado")
            
        else:
            campos.append((id_, payload[i+4:i+4+tamanho]))

        i = i + 4 + tamanho

    return campos

