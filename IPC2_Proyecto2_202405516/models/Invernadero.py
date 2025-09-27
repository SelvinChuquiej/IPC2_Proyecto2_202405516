from models.ListaEnlazada import ListaEnlazada
from models.Hilera import Hilera

class Invernadero:
    def __init__(self, nombre, num_hileras, plantas_x_hilera):
        self.nombre = nombre
        self.num_hileras = num_hileras
        self.plantas_x_hilera = plantas_x_hilera 
        self.hileras = ListaEnlazada()
        self.drones = ListaEnlazada()
        self.planes_riego = ListaEnlazada() 

        for i in range(1, num_hileras + 1):
            self.hileras.insertar(Hilera(i, plantas_x_hilera))

    def agregar_planta(self, planta):
        for hilera in self.hileras:
            if hilera.numero == planta.hilera:
                hilera.agregar_planta(planta)
                return hilera
        return None

    def obtener_hilera(self, numero_hilera):
        for hilera in self.hileras:
            if hilera.numero == numero_hilera:
                return hilera
        return None
    
    def asignar_dron(self, dron, numero_hilera):
        hilera = self.obtener_hilera(numero_hilera)
        if hilera:
            dron.hilera_asignada = numero_hilera 
            hilera.dron_asignado = dron
            self.drones.insertar(dron)
