from typing import List
from logica.custo.posicionamento import simular_ordem
from models.placa import Placa


def obter_pecas_da_placa(placa: Placa):
    """
    Retorna todas as peças já posicionadas na placa.
    Basicamente só percorre prateleiras e coleta cada peça.
    """
    pecas = []

    for prateleira in placa.prateleiras:
        for peca in prateleira.pecas:
            pecas.append(peca)

    return pecas



def calcular_custo_energia(placa: Placa):
    """
    Calcula o custo de energia baseado no modelo simplificado:

      1) Dimensão máxima ocupada na placa
      2) Cortes verticais = saltos no eixo X
      3) Cortes horizontais = saltos no eixo Y
      4) Perímetro externo do layout

    O valor final é multiplicado por 0.01 para converter em reais.
    """

    pecas = obter_pecas_da_placa(placa)

    if len(pecas) == 0:
        return 0

    # -------------------------------------------------------
    # 1) Determinar ocupação máxima na placa
    # -------------------------------------------------------
    maior_x = 0
    maior_y = 0

    for peca in pecas:
        extremidade_direita = peca.x + peca.largura
        extremidade_superior = peca.y + peca.altura

        maior_x = max(maior_x, extremidade_direita)
        maior_y = max(maior_y, extremidade_superior)

    largura_total_ocupada = maior_x
    altura_total_ocupada = maior_y

    # -------------------------------------------------------
    # 2) Cortes verticais 
    # -------------------------------------------------------
    cortes_verticais = []

    pecas_x = sorted(pecas, key=lambda p: p.x)

    for i in range(1, len(pecas_x)):
        p_ant = pecas_x[i - 1]
        p_atual = pecas_x[i]

        limite = p_ant.x + p_ant.largura

        # Existe "buraco" antes da próxima peça?
        if p_atual.x > limite:
            cortes_verticais.append(altura_total_ocupada)

    # -------------------------------------------------------
    # 3) Cortes horizontais 
    # -------------------------------------------------------
    cortes_horizontais = []

    pecas_y = sorted(pecas, key=lambda p: p.y)

    for i in range(1, len(pecas_y)):
        p_ant = pecas_y[i - 1]
        p_atual = pecas_y[i]

        limite = p_ant.y + p_ant.altura

        if p_atual.y > limite:
            cortes_horizontais.append(largura_total_ocupada)

    # -------------------------------------------------------
    # 4) Perímetro externo (somado ao custo)
    # -------------------------------------------------------
    perimetro_externo = 2 * largura_total_ocupada + 2 * altura_total_ocupada

    energia_bruta = (
        sum(cortes_verticais)
        + sum(cortes_horizontais)
        + perimetro_externo
    )

    return energia_bruta * 0.01

def custo_total_para_ordem(ordem_pecas,altura_placa,largura_placa,custo_placa=1000):
    
    """
    Executa o posicionamento das peças na ordem fornecida,
    calcula:
        - custo de matéria-prima (custo_placa * qtd_placas)
        - custo de energia calculado peça a peça

    Retorna:
        (custo_total, numero_de_placas, lista_de_placas)
    """

    lista_de_placas: List[Placa] = simular_ordem(
        ordem_pecas,
        altura_placa,
        largura_placa
    )

    # Custo de matéria-prima = número de placas usadas
    custo_materia_prima = len(lista_de_placas) * custo_placa

    # Energia de corte por placa
    custo_energia = sum(calcular_custo_energia(p) for p in lista_de_placas)

    custo_total = custo_materia_prima + custo_energia

    return custo_total, len(lista_de_placas), lista_de_placas
