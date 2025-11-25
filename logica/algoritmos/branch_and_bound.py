import time
from typing import List, Optional, Tuple

from ..custo.avaliador import custo_total_para_ordem


class BranchAndBound:
    """
    Branch & Bound para o problema de corte de peças.
    Compatível com Placa / Prateleira / Peca já existentes.
    """

    def __init__(self, largura_util: int = 280, altura_util: int = 280):
        self.largura_util = largura_util
        self.altura_util = altura_util

        # melhor solução encontrada até agora
        self.melhor_custo: float = float("inf")
        self.melhor_ordem: Optional[List] = None
        self.melhor_layout = None
        self.melhor_num_placas: Optional[int] = None

        # métricas para diagnóstico
        self.nos_explorados: int = 0
        self.nos_podados: int = 0

        # controle de timeout
        self._tempo_inicio: Optional[float] = None
        self._tempo_limite_seg: Optional[float] = None

    # ---------------------------
    # utilitários
    # ---------------------------

    def _area_da_peca(self, peca) -> int:
        return peca.altura * peca.largura

    def _ordenar_por_area_decrescente(self, pecas: List) -> List:
        """Retorna nova lista ordenada por área (maior -> menor)."""
        return sorted(pecas, key=self._area_da_peca, reverse=True)

    def _timeout_ultrapassado(self) -> bool:
        if self._tempo_limite_seg is None:
            return False
        return (time.perf_counter() - self._tempo_inicio) > self._tempo_limite_seg

    # ---------------------------
    # bounds (lower bound para peças restantes)
    # ---------------------------

    def estimativa_custo_minimo_restante(self, pecas_restantes: List) -> float:
        """
        Estimativa otimista (lower bound) do custo necessário para alocar
        as peças restantes. Base simples: área total / área placa.
        """
        if not pecas_restantes:
            return 0.0

        area_total = sum(p.altura * p.largura for p in pecas_restantes)
        area_placa = self.altura_util * self.largura_util

        # número mínimo de placas necessário (arredondar pra cima)
        placas_minimas = (area_total + area_placa - 1) // area_placa
        placas_minimas = max(1, placas_minimas)  # >= 1

        custo_material_minimo = placas_minimas * 1000.0

        # estimativa muito conservadora de energia (não superestima)
        custo_energia_minimo = placas_minimas * (self.altura_util * 0.01)

        return custo_material_minimo + custo_energia_minimo

    # ---------------------------
    # heurística rápida (UB)
    # ---------------------------

    def heuristica_gulosa_custo(self, pecas: List) -> Tuple[float, int, object]:
        """
        Produz um upper bound inicial usando ordenação por área decrescente
        e a rotina de simulação existente.
        """
        ordem_gulosa = self._ordenar_por_area_decrescente(pecas)
        return custo_total_para_ordem(ordem_gulosa, self.largura_util, self.altura_util)

    # ---------------------------
    # recursão do B&B
    # ---------------------------

    def _branch_recursivo(self, ordem_atual: List, restantes: List):
        """
        Expande prefixos: calcula custo parcial do prefixo (custo real)
        + estimativa otimista para restantes. Poda quando lower bound >= melhor.
        """

        # timeout
        if self._timeout_ultrapassado():
            return

        self.nos_explorados += 1

        # caso base: avaliamos solução completa
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

        # custo parcial real para o prefixo atual
        custo_parcial_atual, placas_parciais, layout_parcial = custo_total_para_ordem(
            ordem_atual, self.largura_util, self.altura_util
        )

        # poda imediata se já é pior que o melhor atual
        if custo_parcial_atual >= self.melhor_custo:
            self.nos_podados += 1
            return

        # estimativa otimista para o restante
        estimativa_restante = self.estimativa_custo_minimo_restante(restantes)
        lower_bound_total = custo_parcial_atual + estimativa_restante

        # poda se nem o melhor caso possível melhora a solução atual
        if lower_bound_total >= self.melhor_custo:
            self.nos_podados += 1
            return

        # gerar filhos: expandir com peças maiores primeiro (heurística)
        filhos_ordenados = self._ordenar_por_area_decrescente(restantes)

        for peca in filhos_ordenados:
            if self._timeout_ultrapassado():
                return

            nova_ordem = ordem_atual + [peca]

            # remove apenas a primeira ocorrência (mantém estabilidade com objetos iguais)
            novos_restantes = []
            removida = False
            for r in restantes:
                if (not removida) and (r is peca):
                    removida = True
                    continue
                novos_restantes.append(r)

            # recursão
            self._branch_recursivo(nova_ordem, novos_restantes)

    # ---------------------------
    # interface pública
    # ---------------------------

    def resolver(
        self,
        lista_pecas: List,
        tempo_limite_seg: Optional[float] = None,
        usar_heuristica_ub: bool = True
    ) -> Tuple[float, Optional[int], object, int]:
        """
        Executa Branch & Bound e retorna:
            (melhor_custo, melhor_num_placas, melhor_layout, nos_explorados)
        """

        # inicializa timeout
        self._tempo_inicio = time.perf_counter()
        self._tempo_limite_seg = tempo_limite_seg

        # reset métricas
        self.nos_explorados = 0
        self.nos_podados = 0

        # UB inicial (heurística gulosa) — útil para poda precoce
        if usar_heuristica_ub:
            custo_guloso, nump_guloso, layout_guloso = self.heuristica_gulosa_custo(lista_pecas)
            self.melhor_custo = custo_guloso
            self.melhor_ordem = self._ordenar_por_area_decrescente(lista_pecas)
            self.melhor_layout = layout_guloso
            self.melhor_num_placas = nump_guloso
        else:
            custo_fallback, nump_fallback, layout_fallback = custo_total_para_ordem(
                lista_pecas, self.largura_util, self.altura_util
            )
            self.melhor_custo = custo_fallback
            self.melhor_ordem = lista_pecas[:]
            self.melhor_layout = layout_fallback
            self.melhor_num_placas = nump_fallback

        # reordena restantes para explorar primeiros ramos promissores
        lista_inicial_restantes = self._ordenar_por_area_decrescente(lista_pecas)

        # chama recursão
        self._branch_recursivo([], lista_inicial_restantes)

        # retorno (compatível com brute-force)
        return self.melhor_custo, self.melhor_num_placas, self.melhor_layout, self.nos_explorados
