# models/peca.py

class Peca:
    """
    Representa uma peça retangular.
    A posição (x, y) é definida quando a peça é colocada em uma prateleira.
    """

    def __init__(self, altura: int, largura: int):
        self.altura = altura
        self.largura = largura
        self.x = 0
        self.y = 0

    def __repr__(self):
        return f"Peca(h={self.altura}, w={self.largura}, x={self.x}, y={self.y})"
