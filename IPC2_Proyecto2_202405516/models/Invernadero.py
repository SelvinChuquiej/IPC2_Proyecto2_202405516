from models.ListaEnlazada import ListaEnlazada

class Invernadero:
    def __init__(self, nombre, num_hileras, plantas_x_hilera):
        self.nombre = nombre
        self.num_hileras = num_hileras
        self.plantas_x_hilera = plantas_x_hilera 
        self.hileras = ListaEnlazada()
        self.drones = ListaEnlazada()
        self.planes_riego = ListaEnlazada() 