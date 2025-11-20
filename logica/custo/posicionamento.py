# logica/posicionamento.py

from typing import List
from models.placa import Placa
from models.peca import Peca
import copy


def simular_ordem(pecas_ordem: List[Peca], largura_util: int = 280, altura_util: int = 280) -> List[Placa]:
    """
    Simula o posicionamento das peças na ordem dada.
    IMPORTANTE: cada simulação trabalha com cópias das peças para não modificar os objetos originais.
    Retorna a lista de placas com as peças posicionadas.
    """

    # Criamos cópias das peças para esta simulação (reseta x,y)
    pecas_copia: List[Peca] = [Peca(p.altura, p.largura) for p in pecas_ordem]

    placas_usadas: List[Placa] = []

    placa_atual = Placa(altura_util=altura_util, largura_util=largura_util)
    placas_usadas.append(placa_atual)

    for peca in pecas_copia:
        colocado = placa_atual.tentar_colocar(peca)

        if not colocado:
            # cria nova placa e tenta novamente
            placa_atual = Placa(altura_util=altura_util, largura_util=largura_util)
            placas_usadas.append(placa_atual)

            colocado2 = placa_atual.tentar_colocar(peca)
            if not colocado2:
                # a peça é maior que a área útil da placa
                raise ValueError(
                    f"Peça {peca.altura}x{peca.largura} maior que área útil da placa ({altura_util}x{largura_util})"
                )

    return placas_usadas
