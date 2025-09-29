from .Nodo import Nodo

# Para procesar instrucciones en orden de llegada plan de riego y simulación

class Cola:
    def __init__(self):
        self.primero = None
        self.ultimo = None
        self.size = 0

    def encolar(self, dato):
        nuevo = Nodo(dato)
        if self.primero is None:
            self.primero = self.ultimo = nuevo
        else: 
            self.ultimo.siguiente = nuevo
            self.ultimo = nuevo
        self.size += 1

    def desencolar(self):
        if self.primero is None:
            return None
        actual = self.primero
        self.primero = self.primero.siguiente
        if self.primero is None:
            self.ultimo = None
        self.size -= 1
        return actual.dato
    
    def estaVacia(self):
        if self.primero is None:
            return True
        else: 
            return False
        
    def __len__(self):
        return self.size
    
    def __iter__(self):
        actual = self.primero
        while actual:
            yield actual.dato
            actual = actual.siguiente

    def ver_frente(self):
        if self.primero:
            return self.primero.dato
        return None
    
    def tamanio(self):
        contador = 0
        actual = self.primero
        while actual:
            contador += 1
            actual = actual.siguiente
        return contador