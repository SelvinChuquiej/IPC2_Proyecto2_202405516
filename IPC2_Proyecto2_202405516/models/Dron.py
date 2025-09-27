class Dron:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre
        self.hilera_asignada = None
        self.posicion_actual = 0
        self.agua_usada = 0
        self.fertilizante_usado = 0
        self.estado = "inicio"

    def mover_adelante(self):
        self.posicion_actual += 1
        self.estado = "moviendo"
        return f"Adelante H{self.hilera_asignada}-P{self.posicion_actual}"

    def mover_atras(self):
        self.posicion_actual -= 1
        self.estado = "moviendo"
        return f"Atras H{self.hilera_asignada}-P{self.posicion_actual}"

    def regar_planta(self, planta):
        self.agua_usada += planta.lt_agua
        self.fertilizante_usado += planta.gr_fertilizante
        self.estado = "regando"
        planta.regada = True
        return f"Regar planta H{planta.hilera}-P{planta.posicion}"

    def esperar(self):
        self.estado = "esperando"
        return "Esperar"
    
    def finalizar(self):
        self.estado = "finalizado"
        return "Finalizar"