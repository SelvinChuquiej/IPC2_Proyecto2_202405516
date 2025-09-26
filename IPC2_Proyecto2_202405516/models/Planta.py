class Planta:
    def __init__(self, hilera, posicion, lt_agua, gr_fertilizante, nombre=""):
        self.hilera = hilera
        self.posicion = posicion
        self.lt_agua = lt_agua
        self.gr_fertilizante = gr_fertilizante
        self.nombre = nombre
        self.regada = False

    def __str__(self):
        return f"Planta H{self.hilera}-P{self.posicion}"