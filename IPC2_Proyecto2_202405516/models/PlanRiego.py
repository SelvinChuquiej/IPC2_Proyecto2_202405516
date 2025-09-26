from models.Cola import Cola
from models.ListaEnlazada import ListaEnlazada

class PlanRiego:
    def __init__(self, nombre, instrucciones_texto):
        self.nombre = nombre
        self.instrucciones_original = instrucciones_texto
        self.cola_instrucciones = Cola()
        self.instrucciones_procesadas = ListaEnlazada()