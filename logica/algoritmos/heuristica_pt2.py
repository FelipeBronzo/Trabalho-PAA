from typing import List


def heuristica_gulosa_particao(pesos: List[float]):
    """
    Heurística gulosa simples para o problema de partição.

    Estratégia:
      - Ordena os itens do maior para o menor.
      - Cada item é colocado no grupo que estiver com a soma menor no momento.

    Retorna:
      (diferenca, indices_grupo1, indices_grupo2, tempo_execucao)
    """
    import time
    inicio = time.perf_counter()

    # Guarda os pesos com seus índices originais
    itens_ordenados = list(enumerate(pesos))
    itens_ordenados.sort(key=lambda x: x[1], reverse=True)

    soma_g1 = 0.0
    soma_g2 = 0.0
    grupo1 = []
    grupo2 = []

    # Distribui os itens tentando sempre balancear
    for indice, peso in itens_ordenados:
        if soma_g1 <= soma_g2:
            grupo1.append(indice)
            soma_g1 += peso
        else:
            grupo2.append(indice)
            soma_g2 += peso

    diferenca = abs(soma_g1 - soma_g2)
    fim = time.perf_counter()

    return diferenca, grupo1, grupo2, fim - inicio
