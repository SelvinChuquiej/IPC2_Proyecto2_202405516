from models.ListaEnlazada import ListaEnlazada

class Hilera:
    def __init__(self, numero, plantas_x_hilera):
        self.numero = numero
        self.plantas_x_hilera = plantas_x_hilera
        self.plantas = ListaEnlazada()
        self.dron_asignado = None