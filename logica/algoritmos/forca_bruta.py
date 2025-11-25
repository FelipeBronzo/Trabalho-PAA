import itertools
import time
from typing import List
from models.peca import Peca
from logica.custo.avaliador import custo_total_para_ordem


def melhor_solucao_forca_bruta(pecas: List[Peca],largura_util: int = 280,altura_util: int = 280,tempo_limite_seg: float = None):

    """
    Gera todas as permutações possíveis das peças e retorna:
        (melhor_custo, numero_de_placas, melhor_layout, total_de_permutacoes)

    Se tempo_limite_seg for fornecido, a busca é interrompida ao estourar o limite.
    """

    numero_de_pecas = len(pecas)

    melhor_custo = float("inf")
    melhor_layout = None
    melhor_numero_de_placas = None

    inicio = time.perf_counter()
    total_de_permutacoes = 0

    # Permutação completa das peças (n! cenários)
    for permutacao in itertools.permutations(pecas, numero_de_pecas):
        total_de_permutacoes += 1

        # Interrompe se houver limite de tempo
        if tempo_limite_seg is not None:
            if time.perf_counter() - inicio > tempo_limite_seg:
                print(
                    f"[brute_force] Tempo limite atingido após "
                    f"{total_de_permutacoes} permutações."
                )
                break

        # Avalia o custo dessa ordem
        custo, numero_de_placas, placas = custo_total_para_ordem(
            list(permutacao), largura_util, altura_util
        )

        # Guarda a melhor solução encontrada
        if custo < melhor_custo:
            melhor_custo = custo
            melhor_layout = placas
            melhor_numero_de_placas = numero_de_placas

    dur = time.perf_counter() - inicio

    return melhor_custo, melhor_numero_de_placas, melhor_layout, total_de_permutacoes
