from models.Cola import Cola
from models.ListaEnlazada import ListaEnlazada

class PlanRiego:
    def __init__(self, nombre, instrucciones_texto):
        self.nombre = nombre
        self.instrucciones_original = instrucciones_texto
        self.cola_instrucciones = Cola()
        self.instrucciones_procesadas = ListaEnlazada()
        self.cargar_instrucciones(instrucciones_texto)

    def cargar_instrucciones(self, texto):
        instrucciones = texto.split(", ")
        for inst in instrucciones:
            inst_limpia = inst.strip()
            if self.validar_formato(inst_limpia):
                self.cola_instrucciones.encolar(inst_limpia)
    
    def validar_formato(self, instruccion):
        # Validar que sea "HX-PY"
        partes = instruccion.split('-')
        if len(partes) != 2:
            return False
        return partes[0].startswith('H') and partes[1].startswith('P')
    
    def siguiente_instruccion(self):
        if not self.cola_instrucciones.esta_vacia():
            inst = self.cola_instrucciones.desencolar()
            self.instrucciones_procesadas.agregar(inst)
            return inst
        return None
    
    def instrucciones_restantes(self):
        return len(self.cola_instrucciones)
    
    def esta_completado(self):
        return self.cola_instrucciones.esta_vacia()
    
    def __str__(self):
        return f"Plan '{self.nombre}' - Instrucciones: {self.instrucciones_original}"