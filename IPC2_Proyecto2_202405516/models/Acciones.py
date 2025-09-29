from models.ListaEnlazada import ListaEnlazada

class AccionDron:
    def __init__(self, nombre_dron, accion):
        self.nombre_dron = nombre_dron
        self.accion = accion

class AccionesSegundo:
    def __init__(self, segundo):
        self.segundo = segundo
        self.acciones = ListaEnlazada()  