from models.ListaEnlazada import ListaEnlazada

class Hilera:
    def __init__(self, numero, plantas_x_hilera):
        self.numero = numero
        self.plantas_x_hilera = plantas_x_hilera
        self.plantas = ListaEnlazada()
        self.dron_asignado = None

    def agregar_planta(self, planta):
        if planta.hilera == self.numero:
            self.plantas.insertar(planta)

    def obtener_planta(self, posicion):
        for planta in self.plantas:
            if planta.posicion == posicion:
                return planta
        return None
    
    def __str__(self):
        return f"Hilera {self.numero} ({len(self.plantas)} plantas)"