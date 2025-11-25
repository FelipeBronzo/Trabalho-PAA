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

    # Copiamos as peças para evitar mexer nos objetos originais
    pecas_copia: List[Peca] = [Peca(p.altura, p.largura) for p in pecas]

    # Ordenação padrão do BFDH: maior altura primeiro (e maior largura em caso de empate)
    pecas_copia.sort(key=lambda p: (-p.altura, -p.largura))

    placas: List[Placa] = []
    placas.append(Placa(altura_util=altura_util, largura_util=largura_util))  # começa com uma placa vazia

    for peca in pecas_copia:
        colocado = False

        # ---------- 1) tenta encaixar em prateleiras já existentes ----------
        melhor_prateleira = None
        melhor_placa = None
        melhor_sobra = None  # quanto menos sobra horizontal, melhor

        for placa in placas:
            for pr in placa.prateleiras:
                if pr.cabe_na_prateleira(peca, placa.largura_util):
                    sobra = placa.largura_util - (pr.x_usado + peca.largura)
                    if sobra < 0:
                        continue
                    # guarda a prateleira que deixar a menor sobra possível
                    if (melhor_sobra is None) or (sobra < melhor_sobra):
                        melhor_sobra = sobra
                        melhor_prateleira = pr
                        melhor_placa = placa

        # se encontrou prateleira adequada, só insere e passa pra próxima peça
        if melhor_prateleira is not None:
            melhor_prateleira.inserir_na_prateleira(peca)
            continue

        # ---------- 2) cria nova prateleira em alguma placa existente ----------
        melhor_placa_para_nova = None
        melhor_sobra_vertical = None

        for placa in placas:
            altura_ocupada = sum(pr.altura for pr in placa.prateleiras)
            altura_restante = placa.altura_util - altura_ocupada

            # verifica se a peça cabe verticalmente e horizontalmente
            if peca.altura <= altura_restante and peca.largura <= placa.largura_util:
                sobra_vertical = altura_restante - peca.altura
                # escolhe a placa que desperdiça menos altura
                if (melhor_sobra_vertical is None) or (sobra_vertical < melhor_sobra_vertical):
                    melhor_sobra_vertical = sobra_vertical
                    melhor_placa_para_nova = placa

        if melhor_placa_para_nova is not None:
            # criar a prateleira já cuida da inserção
            melhor_placa_para_nova.criar_prateleira(peca)
            continue

        # ---------- 3) nenhuma placa comporta → criar placa nova ----------
        nova_placa = Placa(altura_util=altura_util, largura_util=largura_util)
        placas.append(nova_placa)

        # aqui só dá erro se a peça realmente não couber na placa
        if not nova_placa.criar_prateleira(peca):
            raise ValueError(
                f"Peça {peca.altura}x{peca.largura} maior que área útil ({altura_util}x{largura_util})"
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
