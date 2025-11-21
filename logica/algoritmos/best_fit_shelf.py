# logica/algoritmos/best_fit_shelf.py

from typing import List, Tuple
from models.peca import Peca
from models.placa import Placa
from logica.custo.avaliador import calcular_custo_energia
import copy

def simular_ordem_bestfit(pecas: List[Peca], largura_util: int = 280, altura_util: int = 280) -> List[Placa]:
    """
    Simula posicionamento usando Best-Fit Shelf com ordenação por altura decrescente (BFDH).
    Estratégia:
    - Ordena peças por altura decrescente.
    - Para cada peça:
        1) procura entre todas as prateleiras de todas as placas a prateleira onde a peça couber
           e que minimize o espaço sobrando horizontal (best-fit).
        2) se não houver prateleira existente, tenta criar uma nova prateleira em alguma placa
           que possua espaço vertical suficiente — escolhe a placa que minimize o espaço vertical sobrando.
        3) se nenhuma placa existente comportar, cria uma nova placa e insere.
    Retorna lista de placas com peças posicionadas (objetos Placa contendo Prateleira e Peca).
    """

    # Trabalha com cópias das peças para não alterar objetos originais
    pecas_copia: List[Peca] = [Peca(p.altura, p.largura) for p in pecas]

    # Ordena por altura decrescente (tiebreaker por largura decrescente)
    pecas_copia.sort(key=lambda p: (-p.altura, -p.largura))

    placas: List[Placa] = []
    # inicia com uma placa vazia
    placas.append(Placa(altura_util=altura_util, largura_util=largura_util))

    for peca in pecas_copia:
        colocado = False

        # ---------- 1) procurar melhor prateleira existente entre todas as placas ----------
        melhor_prateleira = None
        melhor_placa = None
        melhor_sobra = None  # menor sobra horizontal >= 0

        for placa in placas:
            for pr in placa.prateleiras:
                if pr.cabe_na_prateleira(peca, placa.largura_util):
                    sobra = placa.largura_util - (pr.x_usado + peca.largura)
                    if sobra < 0:
                        continue
                    if (melhor_sobra is None) or (sobra < melhor_sobra):
                        melhor_sobra = sobra
                        melhor_prateleira = pr
                        melhor_placa = placa

        if melhor_prateleira is not None and melhor_placa is not None:
            # inserir na melhor prateleira encontrada
            melhor_prateleira.inserir_na_prateleira(peca)
            colocado = True

        if colocado:
            continue

        # ---------- 2) tentar criar nova prateleira em uma placa existente ----------
        # Escolher placa que permita a criação da prateleira e que minimize sobra vertical
        # (sobra_vertical = remaining_height_after - peca.altura)
        melhor_placa_para_nova = None
        melhor_sobra_vertical = None

        for placa in placas:
            # calcula altura já ocupada
            altura_ocupada = sum(pr.altura for pr in placa.prateleiras)
            altura_restante = placa.altura_util - altura_ocupada

            # cabe verticalmente e cabe horizontalmente (largura)
            if peca.altura <= altura_restante and peca.largura <= placa.largura_util:
                sobra_vertical = altura_restante - peca.altura
                if (best := best if False else None) is None:  # trick para evitar linter sem efeito
                    pass
                if (melhor_sobra_vertical is None) or (sobra_vertical < melhor_sobra_vertical):
                    melhor_sobra_vertical = sobra_vertical
                    melhor_placa_para_nova = placa

        if melhor_placa_para_nova is not None:
            # cria prateleira e insere (Placa.criar_prateleira já insere e registra)
            sucesso = melhor_placa_para_nova.criar_prateleira(peca)
            if not sucesso:
                # fallback defensivo (não deveria acontecer pois já checamos)
                pass
            colocado = True

        if colocado:
            continue

        # ---------- 3) criar nova placa e inserir (deve sempre caber, a não ser que peça seja maior que placa) ----------
        nova_placa = Placa(altura_util=altura_util, largura_util=largura_util)
        placas.append(nova_placa)

        sucesso = nova_placa.criar_prateleira(peca)
        if not sucesso:
            # peça é maior que área útil da placa
            raise ValueError(
                f"Peça {peca.altura}x{peca.largura} maior que área útil da placa ({altura_util}x{largura_util})"
            )

    return placas


def melhor_solucao_best_fit(pecas: List[Peca], largura_util: int = 280, altura_util: int = 280, custo_placa: float = 1000.0) -> Tuple[float, int, List[Placa]]:
    """
    Executa a heurística Best-Fit Decreasing (shelf) e retorna:
      (custo_total_em_reais, numero_de_placas, layout_lista_de_placas)
    Compatível com a assinatura do brute-force (melhor_solucao_forca_bruta).
    """

    placas = simular_ordem_bestfit(pecas, largura_util=largura_util, altura_util=altura_util)

    custo_materia_prima = len(placas) * custo_placa

    custo_energia = 0.0
    for placa in placas:
        custo_energia += calcular_custo_energia(placa)

    custo_total = custo_materia_prima + custo_energia

    return custo_total, len(placas), placas
