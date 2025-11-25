from typing import List
from .prateleira import Prateleira
from .peca import Peca


class Placa:
    """
    Representa uma placa de corte utilizando o método de prateleiras.
    Cada prateleira é empilhada verticalmente até atingir a altura útil da placa.
    """

    def __init__(self, altura_util: int, largura_util: int):
        self.altura_util = altura_util
        self.largura_util = largura_util
        self.prateleiras: List[Prateleira] = []

    def tentar_colocar(self, peca: Peca) -> bool:
        """
        Tenta colocar a peça em uma das prateleiras existentes.
        Se não couber, tenta criar uma nova prateleira.
        """

        # primeiro tenta encaixar nas prateleiras já existentes
        for prateleira in self.prateleiras:
            if prateleira.cabe_na_prateleira(peca, self.largura_util):
                prateleira.inserir_na_prateleira(peca)
                return True

        # se não coube em nenhuma → tenta criar prateleira nova
        return self.criar_prateleira(peca)

    def criar_prateleira(self, peca: Peca) -> bool:
        """
        Empilha uma nova prateleira e tenta inserir a peça nela.
        Retorna False se não for possível (altura excedida ou largura insuficiente).
        """

        # soma das alturas das prateleiras já existentes (define o y da nova)
        soma_y = sum(pr.altura for pr in self.prateleiras)

        # se a nova prateleira ultrapassa a altura da placa → não cabe
        if soma_y + peca.altura > self.altura_util:
            return False

        nova_prateleira = Prateleira(y_inicial=soma_y)

        # se a peça não couber nem na largura da placa, falha
        if not nova_prateleira.cabe_na_prateleira(peca, self.largura_util):
            return False

        # insere e registra a nova prateleira
        nova_prateleira.inserir_na_prateleira(peca)
        self.prateleiras.append(nova_prateleira)
        return True
