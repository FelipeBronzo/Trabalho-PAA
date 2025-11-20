# arquivo: logica/branch_and_bound.py

import time
from typing import List, Optional, Tuple

from ..custo.avaliador import custo_total_para_ordem


class BranchAndBound:
    """
    Branch & Bound para o problema de corte de peças.
    Mantém compatibilidade com as classes existentes (Placa / Prateleira / Peca).
    """

    def __init__(self, largura_util: int = 280, altura_util: int = 280):
        self.largura_util = largura_util
        self.altura_util = altura_util

        # Melhor solução encontrada
        self.melhor_custo: float = float("inf")
        self.melhor_ordem: Optional[List] = None
        self.melhor_layout = None
        self.melhor_num_placas: Optional[int] = None

        # Métricas
        self.nos_explorados: int = 0
        self.nos_podados: int = 0

        # Controle de tempo
        self._tempo_inicio: Optional[float] = None
        self._tempo_limite_seg: Optional[float] = None

    # ---------------------------
    # Funções utilitárias internas
    # ---------------------------

    def _area_da_peca(self, peca) -> int:
        return peca.altura * peca.largura

    def _ordenar_por_area_decrescente(self, pecas: List) -> List:
        """
        Retorna uma nova lista de peças ordenada por área decrescente.
        Usamos função explícita para evitar lambda inline.
        """
        return sorted(pecas, key=self._area_da_peca, reverse=True)

    def _timeout_ultrapassado(self) -> bool:
        if self._tempo_limite_seg is None:
            return False
        return (time.perf_counter() - self._tempo_inicio) > self._tempo_limite_seg

    # ---------------------------
    # Bounds
    # ---------------------------

    def estimativa_custo_minimo_restante(self, pecas_restantes: List) -> float:
        """
        Lower bound (estimativa otimista) para o custo das peças restantes.
        - Usa área total das peças restantes para estimar número mínimo de placas.
        - Computa custo de matéria-prima mínimo e um custo de energia simplificado.
        Essa estimativa é admissível (não superestima o custo real).
        """
        if not pecas_restantes:
            return 0.0

        area_total = 0
        for p in pecas_restantes:
            area_total += p.altura * p.largura

        area_placa = self.altura_util * self.largura_util
        placas_minimas = area_total // area_placa
        if area_total % area_placa != 0:
            placas_minimas += 1
        if placas_minimas < 1:
            placas_minimas = 1

        custo_material_minimo = placas_minimas * 1000.0

        # Estimativa conservadora de energia: assumir pelo menos um corte proporcional à altura
        # por placa. Mantemos valor pequeno para não superestimar.
        custo_energia_minimo = placas_minimas * (self.altura_util * 0.01)

        return custo_material_minimo + custo_energia_minimo

    # ---------------------------
    # Heurística rápida (gulosa)
    # ---------------------------

    def heuristica_gulosa_custo(self, pecas: List) -> Tuple[float, int, object]:
        """
        Heurística rápida para obter um UB (upper bound) inicial.
        Usa ordem por área decrescente e empacotamento com a rotina existente
        (custo_total_para_ordem).
        Retorna (custo, num_placas, layout).
        """
        ordem_gulosa = self._ordenar_por_area_decrescente(pecas)
        custo, num_placas, layout = custo_total_para_ordem(
            ordem_gulosa, self.largura_util, self.altura_util
        )
        return custo, num_placas, layout

    # ---------------------------
    # Branch & Bound recursivo
    # ---------------------------

    def _branch_recursivo(self, ordem_atual: List, restantes: List):
        """
        Função recursiva que expande prefixos. Usa:
        - custo parcial (simulando ordem_atual) para bound real
        - estimativa para restantes
        - poda quando (custo_parcial + estimativa_restante) >= melhor_custo
        """

        # Verifica timeout
        if self._timeout_ultrapassado():
            return

        # Contabiliza nó visitado
        self.nos_explorados += 1

        # Se não há peças restantes, avaliamos solução completa
        if not restantes:
            custo_real, num_placas_real, layout_real = custo_total_para_ordem(
                ordem_atual, self.largura_util, self.altura_util
            )

            if custo_real < self.melhor_custo:
                self.melhor_custo = custo_real
                self.melhor_ordem = ordem_atual[:]
                self.melhor_layout = layout_real
                self.melhor_num_placas = num_placas_real

            return

        # 1) custo parcial real para o prefixo (ótimo para bound)
        # Simulamos apenas a ordem_atual para obter custo parcial das placas já montadas.
        custo_parcial_atual, placas_parciais, layout_parcial = custo_total_para_ordem(
            ordem_atual, self.largura_util, self.altura_util
        )

        # Se o custo parcial já excede a melhor solução, poda imediata
        if custo_parcial_atual >= self.melhor_custo:
            self.nos_podados += 1
            return

        # 2) estimativa otimista para as peças restantes
        estimativa_restante = self.estimativa_custo_minimo_restante(restantes)

        lower_bound_total = custo_parcial_atual + estimativa_restante

        # Podar se o lower bound não puder melhorar a melhor solução atual
        if lower_bound_total >= self.melhor_custo:
            self.nos_podados += 1
            return

        # 3) Gerar filhos em ordem promissora (peças maiores primeiro)
        filhos_ordenados = self._ordenar_por_area_decrescente(restantes)

        for peca in filhos_ordenados:
            if self._timeout_ultrapassado():
                return

            # Construir novos arrays para a chamada recursiva
            nova_ordem = ordem_atual + [peca]

            # Retirar apenas a primeira ocorrência da peça em restantes
            novos_restantes = []
            removida = False
            for r in restantes:
                if (not removida) and (r is peca):
                    removida = True
                    continue
                novos_restantes.append(r)

            self._branch_recursivo(nova_ordem, novos_restantes)

    # ---------------------------
    # Interface pública
    # ---------------------------

    def resolver(
        self,
        lista_pecas: List,
        tempo_limite_seg: Optional[float] = None,
        usar_heuristica_ub: bool = True
    ) -> Tuple[float, Optional[int], object, int]:
        """
        Executa o Branch and Bound.
        Retorna:
            (melhor_custo, melhor_num_placas, melhor_layout, nos_explorados)

        Parâmetros:
        - tempo_limite_seg: se fornecido, interrompe a busca após esse tempo (retorna melhor atual).
        - usar_heuristica_ub: se True, roda a heurística gulosa para obter um UB inicial melhor.
        """

        # inicializa tempo e limite
        self._tempo_inicio = time.perf_counter()
        self._tempo_limite_seg = tempo_limite_seg

        # reinicializa métricas
        self.nos_explorados = 0
        self.nos_podados = 0

        # 1) Upper bound inicial: heurística gulosa opcional
        if usar_heuristica_ub:
            custo_guloso, nump_guloso, layout_guloso = self.heuristica_gulosa_custo(lista_pecas)
            self.melhor_custo = custo_guloso
            self.melhor_ordem = self._ordenar_por_area_decrescente(lista_pecas)
            self.melhor_layout = layout_guloso
            self.melhor_num_placas = nump_guloso
        else:
            # fallback: usa a ordem dada
            custo_fallback, nump_fallback, layout_fallback = custo_total_para_ordem(
                lista_pecas, self.largura_util, self.altura_util
            )
            self.melhor_custo = custo_fallback
            self.melhor_ordem = lista_pecas[:]
            self.melhor_layout = layout_fallback
            self.melhor_num_placas = nump_fallback

        # 2) Opcional: reordenar lista de entrada para explorar ramos melhores primeiro
        #    (usar peças por área decrescente como ordem inicial de expansão)
        lista_inicial_restantes = self._ordenar_por_area_decrescente(lista_pecas)

        # 3) Executa a busca recursiva
        self._branch_recursivo([], lista_inicial_restantes)

        # 4) Retorna métricas (nos_explorados). manter compatibilidade com força bruta:
        #    (melhor_custo, melhor_num_placas, melhor_layout, nos_explorados)
        return self.melhor_custo, self.melhor_num_placas, self.melhor_layout, self.nos_explorados
