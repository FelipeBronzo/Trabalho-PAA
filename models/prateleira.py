# models/prateleira.py

from typing import List
from .peca import Peca


class Prateleira:
    """
    Linha horizontal dentro da placa. As peças são colocadas lado a lado.
    y_inicial: coordenada y onde a prateleira começa (em cm).
    altura: altura fixa da prateleira (igual à da primeira peça inserida).
    x_usado: quanto da largura já foi ocupado (em cm).
    pecas: lista de Peca já posicionadas nesta prateleira.
    """

    def __init__(self, y_inicial: int):
        self.y_inicial = y_inicial
        self.altura = 0
        self.x_usado = 0
        self.pecas: List[Peca] = []

    def cabe_na_prateleira(self, peca: Peca, largura_util_da_placa: int) -> bool:
        
        """
        Retorna True se a peça cabe nesta prateleira, considerando:
        - altura da prateleira (se vazia, admite a altura da peça)
        - espaço horizontal restante (usa largura_util_da_placa fornecida pela placa)
        """

        # Se a prateleira ainda não tem altura definida, ela poderá adotar a altura
        prateleira_altura = self.altura if self.altura > 0 else peca.altura

        # A peça tem altura maior que a prateleira permitida?
        if peca.altura > prateleira_altura:
            return False

        # Encaixa na largura restante da placa?
        if self.x_usado + peca.largura > largura_util_da_placa:
            return False

        return True

    def inserir_na_prateleira(self, peca: Peca) -> None:
        """
        Insere a peça na prateleira: define x,y, atualiza x_usado e lista de peças.
        Pressupõe-se que cabe_na_prateleira já foi chamada e retornou True.
        """

        # Se for a primeira peça, a altura da prateleira vira a altura da peça
        if self.altura == 0:
            self.altura = peca.altura

        # posição horizontal começa em x_usado
        peca.x = self.x_usado

        # posição vertical é o y inicial da prateleira
        peca.y = self.y_inicial

        # atualiza ocupação horizontal
        self.x_usado += peca.largura

        # registra peça na prateleira
        self.pecas.append(peca)
