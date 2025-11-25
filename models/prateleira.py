from typing import List
from .peca import Peca


class Prateleira:
    """
    Linha horizontal dentro da placa onde peças são colocadas lado a lado.

    - y_inicial: posição vertical da prateleira dentro da placa.
    - altura: altura fixa da prateleira (definida pela primeira peça inserida).
    - x_usado: largura já ocupada pela sequência de peças.
    - pecas: lista de peças alocadas nesta prateleira.
    """

    def __init__(self, y_inicial: int):
        self.y_inicial = y_inicial
        self.altura = 0          # definida ao inserir a primeira peça
        self.x_usado = 0         # posição horizontal de inserção
        self.pecas: List[Peca] = []

    def cabe_na_prateleira(self, peca: Peca, largura_util_da_placa: int) -> bool:
        """
        Verifica se a peça cabe nesta prateleira:
        - respeita a altura da prateleira (adotada pela 1ª peça),
        - checa o espaço horizontal disponível da placa.
        """

        # altura da prateleira (se vazia, assume a altura da própria peça)
        prateleira_altura = self.altura if self.altura > 0 else peca.altura

        # se a peça for mais alta que a prateleira, não cabe
        if peca.altura > prateleira_altura:
            return False

        # se ultrapassar a largura da placa, não cabe
        if self.x_usado + peca.largura > largura_util_da_placa:
            return False

        return True

    def inserir_na_prateleira(self, peca: Peca) -> None:
        """
        Insere a peça na prateleira (assume que já cabe).
        Define posições (x, y) e atualiza o espaço ocupado.
        """

        # primeira peça define a altura da prateleira
        if self.altura == 0:
            self.altura = peca.altura

        peca.x = self.x_usado
        peca.y = self.y_inicial

        self.x_usado += peca.largura
        self.pecas.append(peca)
