def crc16_ccitt(dados: str) -> str:
    registrador =  0xFFFF

    dados_bytes = dados.encode("utf-8")
    for byte in dados_bytes:
        metade = byte << 8
        registrador = registrador ^ metade
        
        for _ in range(8):
            if registrador & 0x8000:
                registrador = registrador << 1
                registrador = registrador ^ 0x1021
            else:
                registrador = registrador << 1

            registrador = registrador & 0xFFFF

    return f"{registrador:04X}"
            

        

















 
