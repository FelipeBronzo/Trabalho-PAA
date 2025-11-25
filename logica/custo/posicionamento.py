from typing import List
from models.placa import Placa
from models.peca import Peca
import copy


def simular_ordem(
    pecas_ordem: List[Peca],
    largura_util: int = 280,
    altura_util: int = 280
) -> List[Placa]:
    """
    Simula o posicionamento das peças exatamente na ordem fornecida.
    Cada peça é copiada para evitar que x,y originais sejam modificados.

    Retorna a lista de placas (com suas prateleiras e peças organizadas).
    """

    # Criamos cópias das peças para esta simulação
    # (mantém altura/largura mas reseta posição)
    pecas_copia: List[Peca] = [Peca(p.altura, p.largura) for p in pecas_ordem]

    placas_usadas: List[Placa] = []

    # Começa com a primeira placa
    placa_atual = Placa(altura_util=altura_util, largura_util=largura_util)
    placas_usadas.append(placa_atual)

    for peca in pecas_copia:

        # Primeiro tenta na placa atual
        colocado = placa_atual.tentar_colocar(peca)

        if not colocado:
            # Se não coube, cria nova placa e tenta de novo
            placa_atual = Placa(altura_util=altura_util, largura_util=largura_util)
            placas_usadas.append(placa_atual)

            colocado2 = placa_atual.tentar_colocar(peca)

            # Se ainda assim não couber, a peça é maior que a área útil
            if not colocado2:
                raise ValueError(
                    f"Peça {peca.altura}x{peca.largura} "
                    f"maior que área útil da placa ({altura_util}x{largura_util})"
                )

    return placas_usadas
