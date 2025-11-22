# leitor_arquivo.py
from typing import List
from models.peca import Peca

def ler_pecas(caminho) -> List[Peca]:

    pecas = []

    with open(caminho, "r") as f:
        linhas = [l.strip() for l in f if l.strip()]

    if not linhas:
        return pecas
    
    numero_de_pecas = int(linhas[0])

    for i, linha in enumerate(linhas[1:], start=1):
        partes = linha.split()

        # Formatos aceitos por linha (após o header):
        # - 1 valor: peso (peso-only)
        # - 2 valores: altura largura
        # - 3 valores: altura largura peso
        if len(partes) == 1:
            # apenas peso
            peso = float(partes[0])
            # criamos uma Peca com dimensão mínima e registramos o peso
            # (altura=1, largura=peso) para manter representação retangular
            pecas.append(Peca(1, int(peso) if peso.is_integer() else peso, peso=peso))

        elif len(partes) == 2:
            altura = int(partes[0])
            largura = int(partes[1])
            pecas.append(Peca(altura, largura))

        else:
            altura = int(partes[0])
            largura = int(partes[1])
            peso = float(partes[2])
            pecas.append(Peca(altura, largura, peso=peso))
        
    if len(pecas) != numero_de_pecas:
        print(f"[leitor] Aviso: header indica {numero_de_pecas} peças, mas lidas {len(pecas)}.")
        
    return pecas
