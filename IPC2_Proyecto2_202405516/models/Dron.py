class Dron:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre
        self.hilera_asignada = None
        self.posicion_actual = 0
        self.agua_usada = 0
        self.fertilizante_usado = 0
        self.estado = "inicio"