class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None
        self.completada = 0 
        
    def __str__(self):
        return str(self.dato)