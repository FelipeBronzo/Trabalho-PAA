# models/placa.py

from typing import List
from .prateleira import Prateleira
from .peca import Peca


class Placa:
    """
    Representa uma placa com área útil (altura_util x largura_util).
    Guarda uma lista de prateleiras empilhadas.
    """

    def __init__(self, altura_util: int, largura_util: int):
        self.altura_util = altura_util
        self.largura_util = largura_util
        self.prateleiras: List[Prateleira] = []

    def tentar_colocar(self, peca: Peca) -> bool:
        """
        Tenta colocar a peça em uma prateleira existente.
        Se não couber em nenhuma, tenta criar uma nova prateleira.
        Retorna True se a peça foi colocada nesta placa, False caso contrário.
        """

        # Tentar cada prateleira existente
        for prateleira in self.prateleiras:
            if prateleira.cabe_na_prateleira(peca, self.largura_util):
                prateleira.inserir_na_prateleira(peca)
                return True

        # Não coube em nenhuma prateleira existente -> tentar criar nova
        return self.criar_prateleira(peca)

    def criar_prateleira(self, peca: Peca) -> bool:
        """
        Cria uma nova prateleira empilhada abaixo das existentes e tenta inserir a peça.
        Retorna True se a peça foi inserida, False se não couber verticalmente ou horizontalmente.
        """

        # calcula y inicial da nova prateleira = soma das alturas das prateleiras já existentes
        soma_y = 0
        for pr in self.prateleiras:
            soma_y += pr.altura

        # verifica se a nova prateleira caberia verticalmente
        if soma_y + peca.altura > self.altura_util:
            return False

        # cria a prateleira com o y inicial calculado
        nova_prateleira = Prateleira(y_inicial=soma_y)

        # verifica se cabe horizontalmente na placa (usa largura_util atual)
        if not nova_prateleira.cabe_na_prateleira(peca, self.largura_util):
            return False

        # insere e registra a prateleira
        nova_prateleira.inserir_na_prateleira(peca)
        self.prateleiras.append(nova_prateleira)
        return True
