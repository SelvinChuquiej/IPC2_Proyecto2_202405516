from .Nodo import Nodo

#Utilizado para cualquier colección donde tenga que recorrer, agregar o eliminar elementos dinámicamente.

class ListaEnlazada:
    def __init__(self):
        self.primero = None
        self.ultimo = None
        self.size = 0

    def insertar(self, dato):
        nuevo = Nodo(dato)
        if self.primero is None:
            self.primero = self.ultimo = nuevo
        else:
            self.ultimo.siguiente = nuevo
            self.ultimo = nuevo
        self.size += 1
        return nuevo 

    def buscar(self, dato):
        actual = self.primero
        while actual:
            if actual.dato == dato:
                return actual
            actual = actual.siguiente
        return None
    
    def __len__(self):
        return self.size
    
    def __iter__(self):
        actual = self.primero
        while actual:
            yield actual.dato
            actual = actual.siguiente