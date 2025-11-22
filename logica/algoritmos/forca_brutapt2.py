
"""
Adaptador "Força Bruta PT2" para integrar com a interface.

Este módulo expõe `melhor_solucao_forca_brutapt2` que tenta particionar
o conjunto de peças em dois grupos (por peso) e avalia cada partição
simulando a ordem resultante via o avaliador existente.

Retorna (custo_total, None, layout_lista, particoes_avaliadas)
para compatibilidade com a interface (exibe métricas similares ao brute force).
"""

# NOTE (distinção importante):
# - Este módulo implementa o problema de PARTIÇÃO (parte 2 do trabalho):
#   dado um conjunto de peças, particiona-as em dois grupos (por peso) de
#   forma a minimizar a diferença entre as somas dos dois grupos.
# - A PARTIÇÃO é um problema diferente do problema de CORTE/EMPACOTAMENTO em
#   placas (2D). No corte/empacotamento usamos largura/altura e simulamos
#   posicionamento em placas/placas úteis; esse processo pode lançar erros
#   do tipo "Peça AxB maior que área útil da placa".
# - Aqui (PT2) trabalhamos apenas com pesos (veja `Peca.obter_peso()`): o
#   módulo não realiza simulações de posicionamento nem tenta empacotar em
#   placas. A interface foi atualizada para chamar diretamente as funções de
#   partição (`brute_force_partition`, `branch_and_bound_partition`,
#   `heuristic_greedy_partition`) sem passar as ordens ao avaliador de placas.
# - Mantemos chamadas opcionais ao avaliador apenas quando explicitamente
#   necessário em outras partes do projeto; mas PT2 foi isolado para evitar
#   mensagens/erros relacionados a placas durante a resolução do problema de
#   partição.


import itertools
import time
from typing import List, Tuple

from models.peca import Peca
from logica.custo.avaliador import custo_total_para_ordem


def melhor_solucao_forca_brutapt2(pecas: List[Peca], largura_util: int = 280, altura_util: int = 280, tempo_limite_seg: float = None):
    """
        Variante 'PT2' baseada em partições por peso:
        - Converte as peças para 'pesos' (peso explícito ou área como fallback)
        - Gera todas as partições (evitando duplicatas usando k até n//2)
        - Para cada partição, monta uma ordem (grupo1 seguido de grupo2, peças ordenadas por peso decrescente)
            e avalia o custo usando `custo_total_para_ordem` (apenas para manter compatibilidade de interface).

        Retorna (melhor_custo, None, melhor_layout, particoes_avaliadas)

        OBS: Esta função foi projetada para integrar facilmente com a interface do projeto.
    """

    n = len(pecas)
    if n == 0:
        return 0.0, None, [], 0

    # pesos não são necessários separadamente aqui — calculamos por peça quando preciso

    melhor_custo = float("inf")
    melhor_layout = None

    inicio = time.perf_counter()
    particoes_avaliadas = 0

    # Para evitar duplicatas, apenas gerar combinações de tamanho k até n//2
    indices = list(range(n))

    for k in range((n // 2) + 1):
        # gerar combinações de índices
        for grupo1_indices in itertools.combinations(indices, k):
            particoes_avaliadas += 1

            # checar timeout
            if tempo_limite_seg is not None and (time.perf_counter() - inicio) > tempo_limite_seg:
                # interrompe e retorna o melhor encontrado até o momento
                print(f"[forca_brutapt2] Tempo limite atingido após avaliar {particoes_avaliadas} partições.")
                return melhor_custo, None, melhor_layout, particoes_avaliadas

            grupo1_set = set(grupo1_indices)
            grupo2_indices = [i for i in indices if i not in grupo1_set]

            # ordenar peças dentro de cada grupo por peso decrescente para tentar melhorar packing
            grupo1 = sorted([pecas[i] for i in grupo1_indices], key=lambda p: p.obter_peso(), reverse=True)
            grupo2 = sorted([pecas[i] for i in grupo2_indices], key=lambda p: p.obter_peso(), reverse=True)

            ordem_tentativa = list(grupo1) + list(grupo2)

            try:
                custo, _, layout = custo_total_para_ordem(ordem_tentativa, largura_util, altura_util)
            except Exception as e:
                # se alguma peça não couber, ignorar essa partição
                # (manter robustez semelhante ao restante do código)
                print(f"[forca_brutapt2] erro ao avaliar particao: {e}")
                continue

            if custo < melhor_custo:
                melhor_custo = custo
                melhor_layout = layout

    dur = time.perf_counter() - inicio
    print(f"[forca_brutapt2] Partições avaliadas: {particoes_avaliadas} em {dur:.3f}s")

    return melhor_custo, None, melhor_layout, particoes_avaliadas


# -----------------------------------------------------------------------------
# Implementação do problema de Partição (diferença mínima) — Brute force e
# Branch-and-Bound (para a parte 2 do trabalho). Essas funções operam sobre
# listas de pesos (inteiros ou floats) e fornecem métricas de comparação.
# -----------------------------------------------------------------------------


def brute_force_partition(pesos: List[float]):
    """
    Força bruta para o problema da partição: encontra subconjunto cujo soma
    minimiza a diferença absoluta entre os dois grupos.

    Retorna
      (melhor_diferenca, grupo1_indices, grupo2_indices, particoes_avaliadas)
    onde grupo*_indices são listas de índices na entrada `pesos`.
    """

    n = len(pesos)
    total = sum(pesos)
    melhor_dif = float("inf")
    melhor_g1 = []
    melhor_g2 = []
    particoes = 0

    import math

    # iterar sobre tamanhos até n//2 para evitar duplicatas simétricas
    for k in range((n // 2) + 1):
        for comb in itertools.combinations(range(n), k):
            particoes += 1
            s = sum(pesos[i] for i in comb)
            dif = abs(total - 2 * s)
            if dif < melhor_dif:
                melhor_dif = dif
                melhor_g1 = list(comb)
                melhor_g2 = [i for i in range(n) if i not in set(comb)]

    return melhor_dif, melhor_g1, melhor_g2, particoes


def branch_and_bound_partition(pesos: List[float]):
    """
    Branch and Bound para o problema de partição.

    Estratégia:
      - Ordena itens por peso decrescente (mantendo índices originais)
      - Expande árvore binária (incluir/excluir) em DFS
      - Calcula lower bound otimista: dado soma atual s e soma_restante r,
        o melhor s' possível está em [s, s+r]; se total/2 estiver nesse intervalo
        a diferença mínima possível é 0; senão a diferença mínima possível é
        min(|total-2*s|, |total-2*(s+r)|).
      - Se lower_bound >= melhor_dif_atual, poda o ramo.

    Retorna
      (melhor_dif, grupo1_indices, grupo2_indices, nos_explorados)
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

    # pré-computa prefixos de soma para eficiência (soma dos restos a partir de i)
    prefix_rest = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        prefix_rest[i] = prefix_rest[i + 1] + pesos_ord[i]

    def dfs(i: int, soma_atual: float, escolhidos_ord: List[int]):
        nonlocal melhor_dif, melhor_g1_ord_indices, nos_explorados

        # contador de nós
        nos_explorados += 1

        # bound: soma restante
        soma_restante = prefix_rest[i] if i < n else 0

        # best possible sum for grupo1 está em [soma_atual, soma_atual + soma_restante]
        # lower bound para diferença:
        metade = total / 2.0
        if soma_atual <= metade <= (soma_atual + soma_restante):
            lower = 0.0
        else:
            # se metade está à esquerda do intervalo, escolha extremo mais próximo
            cand1 = abs(total - 2 * soma_atual)
            cand2 = abs(total - 2 * (soma_atual + soma_restante))
            lower = min(cand1, cand2)

        # poda se lower >= melhor_dif já encontrado
        if lower >= melhor_dif:
            return

        # se chegamos ao fim, avalia solução
        if i == n:
            dif = abs(total - 2 * soma_atual)
            if dif < melhor_dif:
                melhor_dif = dif
                melhor_g1_ord_indices = escolhidos_ord.copy()
            return

        # escolha: incluir o item i em grupo1
        dfs(i + 1, soma_atual + pesos_ord[i], escolhidos_ord + [i])

        # escolha: não incluir (item vai para grupo2)
        dfs(i + 1, soma_atual, escolhidos_ord)

    # inicia busca
    dfs(0, 0.0, [])

    # traduz índices ordenados de volta para índices originais
    grupo1 = [idx_ord[i] for i in melhor_g1_ord_indices]
    grupo2 = [i for i in range(n) if i not in grupo1]

    return melhor_dif, grupo1, grupo2, nos_explorados


def comparar_bruteforce_vs_bnb(pesos: List[float]):
    """
    Roda ambos os métodos, compara resultados e tempos. Retorna um dicionário
    com métricas e resultados.
    """
    import time

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

    # consistência
    resultado["consistente"] = abs(resultado["bruteforce"]["melhor_dif"] - resultado["branch_and_bound"]["melhor_dif"]) < 1e-9

    return resultado
