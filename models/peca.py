class Peca:
    """
    Representa uma peça retangular.
    Se peso não for informado, utiliza peso = área / 1000 como default.
    """

    def __init__(self, altura: int, largura: int, peso: float = None):
        self.altura = altura
        self.largura = largura
        self.peso = peso  # usado na parte 2 (porões)
        self.x = 0
        self.y = 0

    def __repr__(self):
        return f"Peca(h={self.altura}, w={self.largura}, peso={self.peso}, x={self.x}, y={self.y})"

    def obter_peso(self) -> float:
        """
        Retorna o peso da peça.
        Usado na Parte 2.
        """
        if self.peso is not None:
            return self.peso

        # peso padrão baseado na área (conversão simples)
        return (self.altura * self.largura) / 1000
