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

        if len(partes) < 2:
            raise ValueError(f"Linha {i+1} do arquivo inválida: '{linha}'")
        
        altura = int(partes[0])
        largura = int(partes[1])
        pecas.append(Peca(altura, largura))
        
    if len(pecas) != numero_de_pecas:
        print(f"[leitor] Aviso: header indica {numero_de_pecas} peças, mas lidas {len(pecas)}.")
        
    return pecas
