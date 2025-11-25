from typing import List, Tuple


def branch_and_bound_particao(pesos: List[float]):
    """
    Branch and Bound para o problema de partição.

    Retorna:
        (melhor_diferenca, grupo1_indices, grupo2_indices, nos_explorados)

    A lógica:
      - Ordena os itens do maior para o menor.
      - Explora a árvore de decisões em profundidade (DFS).
      - Faz poda quando o bound indica que não há chance de melhorar
        a melhor solução encontrada até agora.
    """

    n = len(pesos)
    soma_total = sum(pesos)

    # Junta pesos com índices originais e ordena do maior para o menor
    itens_ordenados = list(enumerate(pesos))
    itens_ordenados.sort(key=lambda x: x[1], reverse=True)

    pesos_ord = [p for (_, p) in itens_ordenados]
    indices_ord = [i for (i, _) in itens_ordenados]

    melhor_diferenca = float("inf")
    melhor_grupo1_ord = []
    nos_explorados = 0

    # soma_restante[i] = soma dos itens do índice i até o fim
    soma_restante = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        soma_restante[i] = soma_restante[i + 1] + pesos_ord[i]

    def dfs(pos: int, soma_atual: float, escolhidos: List[int]):
        nonlocal melhor_diferenca, melhor_grupo1_ord, nos_explorados
        nos_explorados += 1

        # Quanto ainda pode ser adicionado
        restante = soma_restante[pos] if pos < n else 0

        metade = soma_total / 2.0

        # Calcula um lower bound simples para decidir se vale a pena continuar
        if soma_atual <= metade <= (soma_atual + restante):
            bound = 0.0
        else:
            opcao1 = abs(soma_total - 2 * soma_atual)
            opcao2 = abs(soma_total - 2 * (soma_atual + restante))
            bound = min(opcao1, opcao2)

        # Poda: se nem o melhor cenário melhora a melhor solução atual, corta o ramo
        if bound >= melhor_diferenca:
            return

        # Chegou ao fim da árvore
        if pos == n:
            diferenca = abs(soma_total - 2 * soma_atual)
            if diferenca < melhor_diferenca:
                melhor_diferenca = diferenca
                melhor_grupo1_ord = escolhidos.copy()
            return

        # Caso 1: inclui item atual no grupo 1
        dfs(pos + 1, soma_atual + pesos_ord[pos], escolhidos + [pos])

        # Caso 2: não inclui -> item vai para o grupo 2
        dfs(pos + 1, soma_atual, escolhidos)

    # Inicia a busca
    dfs(0, 0.0, [])

    # Reverte os índices para a ordem original dos pesos
    grupo1 = [indices_ord[i] for i in melhor_grupo1_ord]
    grupo2 = [i for i in range(n) if i not in grupo1]

    return melhor_diferenca, grupo1, grupo2, nos_explorados
