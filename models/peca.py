# models/peca.py

class Peca:
    """
    Representa uma peça retangular.
    A posição (x, y) é definida quando a peça é colocada em uma prateleira.
    """

    def __init__(self, altura: int, largura: int, peso: float = None):
        """
        Peca pode opcionalmente conter um atributo `peso`.

        - altura, largura: dimensões usadas para posicionamento/layout.
        - peso: se fornecido, será utilizado pelos algoritmos de partição;
          caso contrário, considera-se peso = altura * largura.
        """
        self.altura = altura
        self.largura = largura
        self.peso = peso
        self.x = 0
        self.y = 0

    def __repr__(self):
        return f"Peca(h={self.altura}, w={self.largura}, peso={self.peso}, x={self.x}, y={self.y})"

    def obter_peso(self) -> float:
        """Retorna o peso desta peça: `peso` se definido, caso contrário `altura * largura`."""
        if hasattr(self, "peso") and self.peso is not None:
            return self.peso
        return (self.altura * self.largura)/1000
