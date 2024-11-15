class Geometry:
    def __init__(self, area=None, volume=None, altura=None,largura=None,profundidade=None):
        self.area = area
        self.volume = volume
        self.altura=altura
        self.largura=largura
        self.profundidade=profundidade

    def __eq__(self, other):
        return (self.area == other.area and 
                self.volume == other.volume and
                self.altura == other.altura and
                self.largura ==other.largura and
                self.profundidade ==other.profundidade)

    def __hash__(self):
        return hash((self.area, self.volume, self.altura,self.largura,self.profundidade))
