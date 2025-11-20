import itertools
import time
from typing import List
from models.peca import Peca
from logica.custo.avaliador import custo_total_para_ordem

def melhor_solucao_forca_bruta(pecas: List[Peca], largura_util: int = 280, altura_util: int = 280, tempo_limite_seg: float = None):

    """
    Gera todas permutações e retorna (melhor_custo, numero_de_placas, melhor_layout).
    tempo_limite_seg: se fornecido, interrompe a busca após esse limite (opcional).
    """

    numero_de_pecas = len(pecas)
    melhor_custo = float("inf")
    melhor_layout = None
    melhor_num_placas = None

    inicio = time.perf_counter()
    total_de_permutacoes = 0

    for permutacao in itertools.permutations(pecas, numero_de_pecas):
        # opcional: checa tempo
        total_de_permutacoes += 1
        if tempo_limite_seg is not None:
            if time.perf_counter() - inicio > tempo_limite_seg:
                print(f"[brute_force] Tempo limite atingido após avaliar {total_de_permutacoes} permutações.")
                break

        custo, numero_de_placas, placas = custo_total_para_ordem(list(permutacao), largura_util, altura_util)

        if custo < melhor_custo:
            melhor_custo = custo
            melhor_layout = placas
            melhor_numero_de_placas = numero_de_placas

    dur = time.perf_counter() - inicio
    print(f"[brute_force] Permutações avaliadas: {total_de_permutacoes} em {dur:.3f}s")
    return melhor_custo, melhor_numero_de_placas, melhor_layout
