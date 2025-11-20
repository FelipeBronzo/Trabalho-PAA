from typing import List
from logica.custo.posicionamento import simular_ordem
from models.placa import Placa


def obter_pecas_da_placa(placa: Placa):

    """
    Retorna todas as peças posicionadas dentro da placa,
    percorrendo prateleiras e coletando suas peças.
    """

    pecas = []

    for prateleira in placa.prateleiras:
        for peca in prateleira.pecas:
            pecas.append(peca)

    return pecas


def calcular_custo_energia(placa: Placa):

    """
    Calcula o custo de energia baseado no modelo aproximado do enunciado.
    A lógica segue três componentes principais:

    1. Dimensões totais ocupadas (altura e largura máxima atingidas)
    2. Cortes verticais entre grupos de peças que não estão na mesma coluna
    3. Cortes horizontais entre grupos de peças que não estão na mesma linha
    """

    pecas = obter_pecas_da_placa(placa)

    if len(pecas) == 0:
        return 0

    # -----------------------------------------------
    # 1. Descobrir dimensões ocupadas
    # -----------------------------------------------
    maior_x = 0
    maior_y = 0

    for peca in pecas:
        extremidade_direita = peca.x + peca.largura
        extremidade_superior = peca.y + peca.altura

        if extremidade_direita > maior_x:
            maior_x = extremidade_direita

        if extremidade_superior > maior_y:
            maior_y = extremidade_superior

    largura_total_ocupada = maior_x
    altura_total_ocupada = maior_y

    # -----------------------------------------------
    # 2. Cortes verticais
    # (ocorrem quando existe um "salto" no eixo X)
    # -----------------------------------------------

    cortes_verticais = []

    pecas_ordenadas_por_x = sorted(pecas, key=lambda p: p.x)

    for indice in range(1, len(pecas_ordenadas_por_x)):
        peca_anterior = pecas_ordenadas_por_x[indice - 1]
        peca_atual = pecas_ordenadas_por_x[indice]

        limite_anterior = peca_anterior.x + peca_anterior.largura

        if peca_atual.x > limite_anterior:
            cortes_verticais.append(altura_total_ocupada)

    # -----------------------------------------------
    # 3. Cortes horizontais
    # (ocorrem quando existe um "salto" no eixo Y)
    # -----------------------------------------------

    cortes_horizontais = []

    pecas_ordenadas_por_y = sorted(pecas, key=lambda p: p.y)

    for indice in range(1, len(pecas_ordenadas_por_y)):
        peca_anterior = pecas_ordenadas_por_y[indice - 1]
        peca_atual = pecas_ordenadas_por_y[indice]

        limite_anterior = peca_anterior.y + peca_anterior.altura

        if peca_atual.y > limite_anterior:
            cortes_horizontais.append(largura_total_ocupada)

    # -----------------------------------------------
    # 4. Perímetro externo do layout
    # (usado no cálculo mostrado no enunciado)
    # -----------------------------------------------

    perimetro_externo = (
        2 * largura_total_ocupada +
        2 * altura_total_ocupada
    )

    # Soma de todas as contribuições
    energia_bruta = (
        sum(cortes_verticais) +
        sum(cortes_horizontais) +
        perimetro_externo
    )

    custo_em_reais = energia_bruta * 0.01

    return custo_em_reais


def custo_total_para_ordem(ordem_pecas, altura_placa, largura_placa, custo_placa=1000):
    """
    Simula a ordem das peças, gera as placas resultantes,
    e calcula:
        - Custo de matéria-prima (custo_placa por placa)
        - Custo de energia baseado no layout
    """

    lista_de_placas: List[Placa] = simular_ordem(ordem_pecas, altura_placa, largura_placa)

    custo_materia_prima = len(lista_de_placas) * custo_placa

    custo_energia = 0

    for placa in lista_de_placas:
        custo_energia += calcular_custo_energia(placa)

    custo_total = custo_materia_prima + custo_energia

    return custo_total, len(lista_de_placas), lista_de_placas

