import itertools
from typing import List


def forca_bruta_particao(pesos: List[float]):
    """
    Força bruta para o problema da partição.

    Varre todas as combinações possíveis (até n//2 para evitar duplicatas)
    e encontra o subconjunto cuja soma deixa a menor diferença possível
    entre os dois grupos.

    Retorna:
      (melhor_diferenca, grupo1, grupo2, particoes_avaliadas)
    """

    qtd = len(pesos)
    soma_total = sum(pesos)

    melhor_diferenca = float("inf")
    melhor_grupo1 = []
    melhor_grupo2 = []
    particoes_avaliadas = 0

    # Percorre subconjuntos de tamanho 0 até n//2
    for k in range((qtd // 2) + 1):
        for combinacao in itertools.combinations(range(qtd), k):
            particoes_avaliadas += 1

            soma_grupo1 = sum(pesos[i] for i in combinacao)
            diferenca = abs(soma_total - 2 * soma_grupo1)

            if diferenca < melhor_diferenca:
                melhor_diferenca = diferenca
                melhor_grupo1 = list(combinacao)
                melhor_grupo2 = [i for i in range(qtd) if i not in melhor_grupo1]

    return melhor_diferenca, melhor_grupo1, melhor_grupo2, particoes_avaliadas
