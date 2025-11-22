"""
Branch-and-Bound (Parte 2) separado do adaptador PT2.

Este módulo contém a implementação do algoritmo Branch-and-Bound para o
problema de partição (minimizar a diferença entre dois grupos). A intenção
é manter a lógica separada de `forca_brutapt2.py` para facilitar testes e
benchmarks.

Ele reutiliza a função `brute_force_partition` definida em
`logica.algoritmos.forca_brutapt2` caso seja necessária comparação.
"""

from typing import List, Tuple
import itertools


def branch_and_bound_partition(pesos: List[float]):
    """
    Branch and Bound para o problema de partição.

    Recebe uma lista de pesos (floats/ints) e retorna:
      (melhor_dif, grupo1_indices, grupo2_indices, nos_explorados)

    A implementação ordena os itens por peso decrescente (mantendo os
    índices originais), explora a árvore de decisões (incluir/excluir)
    em DFS e poda ramos cujo lower bound não pode melhorar a melhor
    solução encontrada até o momento.
    """

    n = len(pesos)
    total = sum(pesos)

    # empacotar pesos com índices e ordenar por peso decrescente
    enumerados = list(enumerate(pesos))
    enumerados.sort(key=lambda x: x[1], reverse=True)  # (idx, peso)

    pesos_ord = [p for (_, p) in enumerados]
    idx_ord = [i for (i, _) in enumerados]

    melhor_dif = float("inf")
    melhor_g1_ord_indices = []
    nos_explorados = 0

    # prefix_rest[i] = soma dos pesos dos itens i..n-1
    prefix_rest = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        prefix_rest[i] = prefix_rest[i + 1] + pesos_ord[i]

    def dfs(i: int, soma_atual: float, escolhidos_ord: List[int]):
        nonlocal melhor_dif, melhor_g1_ord_indices, nos_explorados

        nos_explorados += 1

        soma_restante = prefix_rest[i] if i < n else 0

        metade = total / 2.0
        if soma_atual <= metade <= (soma_atual + soma_restante):
            lower = 0.0
        else:
            cand1 = abs(total - 2 * soma_atual)
            cand2 = abs(total - 2 * (soma_atual + soma_restante))
            lower = min(cand1, cand2)

        if lower >= melhor_dif:
            return

        if i == n:
            dif = abs(total - 2 * soma_atual)
            if dif < melhor_dif:
                melhor_dif = dif
                melhor_g1_ord_indices = escolhidos_ord.copy()
            return

        # incluir item i em grupo1
        dfs(i + 1, soma_atual + pesos_ord[i], escolhidos_ord + [i])

        # não incluir -> vai para grupo2
        dfs(i + 1, soma_atual, escolhidos_ord)

    dfs(0, 0.0, [])

    # traduz índices ordenados de volta para índices originais
    grupo1 = [idx_ord[i] for i in melhor_g1_ord_indices]
    grupo2 = [i for i in range(n) if i not in grupo1]

    return melhor_dif, grupo1, grupo2, nos_explorados


def comparar_com_bruteforce(pesos: List[float]):
    """
    Função utilitária que compara o resultado do B&B com a força bruta.
    Requer que `brute_force_partition` esteja disponível em
    `logica.algoritmos.forca_brutapt2`.

    Retorna um dicionário com métricas e flag de consistência.
    """

    import time
    try:
        from logica.algoritmos.forca_brutapt2 import brute_force_partition
    except Exception as e:
        raise ImportError("Não foi possível importar brute_force_partition: " + str(e))

    t0 = time.perf_counter()
    bf = brute_force_partition(pesos)
    t1 = time.perf_counter()
    bnb = branch_and_bound_partition(pesos)
    t2 = time.perf_counter()

    resultado = {
        "bruteforce": {
            "melhor_dif": bf[0],
            "grupo1": bf[1],
            "grupo2": bf[2],
            "particoes_avaliadas": bf[3],
            "tempo": t1 - t0,
        },
        "branch_and_bound": {
            "melhor_dif": bnb[0],
            "grupo1": bnb[1],
            "grupo2": bnb[2],
            "nos_explorados": bnb[3],
            "tempo": t2 - t1,
        },
    }

    resultado["consistente"] = abs(resultado["bruteforce"]["melhor_dif"] - resultado["branch_and_bound"]["melhor_dif"]) < 1e-9

    return resultado


def heuristic_greedy_partition(pesos: List[float]):
    """
    Heurística gulosa simples para o problema de partição.

    Estratégia:
      - Ordena itens por peso decrescente (mantendo índices originais).
      - Iterativamente atribui cada item ao subconjunto com soma atual menor.

    Retorna (dif, grupo1_indices, grupo2_indices, tempo_exec)
    """
    import time
    t0 = time.perf_counter()

    enumerados = list(enumerate(pesos))
    enumerados.sort(key=lambda x: x[1], reverse=True)

    sum1 = 0.0
    sum2 = 0.0
    g1 = []
    g2 = []

    for idx, peso in enumerados:
        if sum1 <= sum2:
            g1.append(idx)
            sum1 += peso
        else:
            g2.append(idx)
            sum2 += peso

    dif = abs(sum1 - sum2)
    t1 = time.perf_counter()
    return dif, g1, g2, t1 - t0


def comparar_com_heuristica(pesos: List[float]):
    """
    Roda brute-force, branch-and-bound e a heurística gulosa, retornando
    métricas comparativas (diferenças, tempos, consistência).
    """
    import time

    t0 = time.perf_counter()
    try:
        from logica.algoritmos.forca_brutapt2 import brute_force_partition
    except Exception:
        # fallback: import local if available
        from logica.algoritmos.forca_brutapt2 import brute_force_partition

    bf = brute_force_partition(pesos)
    t1 = time.perf_counter()
    bnb = branch_and_bound_partition(pesos)
    t2 = time.perf_counter()
    heur = heuristic_greedy_partition(pesos)

    resultado = {
        "bruteforce": {
            "melhor_dif": bf[0],
            "grupo1": bf[1],
            "grupo2": bf[2],
            "particoes_avaliadas": bf[3],
            "tempo": t1 - t0,
        },
        "branch_and_bound": {
            "melhor_dif": bnb[0],
            "grupo1": bnb[1],
            "grupo2": bnb[2],
            "nos_explorados": bnb[3],
            "tempo": t2 - t1,
        },
        "heuristica_gulosa": {
            "melhor_dif": heur[0],
            "grupo1": heur[1],
            "grupo2": heur[2],
            "tempo": heur[3],
        }
    }

    resultado["consistente_bnb_bf"] = abs(resultado["bruteforce"]["melhor_dif"] - resultado["branch_and_bound"]["melhor_dif"]) < 1e-9
    resultado["heuristica_igual_optimo"] = abs(resultado["bruteforce"]["melhor_dif"] - resultado["heuristica_gulosa"]["melhor_dif"]) < 1e-9

    return resultado


if __name__ == "__main__":
    # teste rápido quando executado diretamente
    import sys
    exemplo = [10, 20, 30, 40, 50] if len(sys.argv) == 1 else list(map(float, sys.argv[1:]))
    print(comparar_com_bruteforce(exemplo))
