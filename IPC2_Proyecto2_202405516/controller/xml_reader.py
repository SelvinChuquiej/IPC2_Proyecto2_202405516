import xml.etree.ElementTree as ET
from models.PlanRiego import PlanRiego
from models.Invernadero import Invernadero
from models.Dron import Dron
from models.Planta import Planta
from models.ListaEnlazada import ListaEnlazada

def leer_archivo(ruta): 

    try:
        tree =  ET.parse(ruta)
        root = tree.getroot()
    except Exception as e:
        print(f"Error al leer el archivo XML: {e}")
        return None, None
    
    lista_drones = ListaEnlazada()
    
    for dron in root.find('listaDrones').findall('dron'):
        id_dron = dron.get('id')
        nombre_dron = dron.get('nombre')
        dronNew = Dron(id_dron, nombre_dron)
        lista_drones.insertar(dronNew)

    lista_invernaderos = ListaEnlazada()

    for invernadero in root.find('listaInvernaderos').findall('invernadero'):
        nombre_inv = invernadero.get('nombre')
        num_hileras = int(invernadero.find('numeroHileras').text)
        plantas_x_hilera = int(invernadero.find('plantasXhilera').text)
        invernaderoNew = Invernadero(nombre_inv, num_hileras, plantas_x_hilera)
        lista_invernaderos.insertar(invernaderoNew)

        for planta in invernadero.find('listaPlantas').findall('planta'):
            hilera_planta = int(planta.get('hilera'))
            posicion_planta = int(planta.get('posicion'))
            ltAgua_planta = int(planta.get('litrosAgua'))
            gmFertilizante_planta = int(planta.get('gramosFertilizante'))
            nombre_planta = planta.text
            plantaNew = Planta(hilera_planta, posicion_planta, ltAgua_planta, gmFertilizante_planta, nombre_planta)
            invernaderoNew.agregar_planta(plantaNew)

        for asignacion in invernadero.find('asignacionDrones').findall('dron'):
            id_dron_asign = asignacion.get('id')
            num_hilera_asign = int(asignacion.get('hilera'))
            dron = None
            for d in lista_drones:
                if d.id == id_dron_asign:
                    dron = d
                    break
            if dron:
                invernaderoNew.asignar_dron(dron, num_hilera_asign)

        for plan in invernadero.find('planesRiego').findall('plan'):
            nombre_plan = plan.get('nombre')
            linstrucciones_plan = plan.text
            planRiegoNew = PlanRiego(nombre_plan, linstrucciones_plan)
            invernaderoNew.planes_riego.insertar(planRiegoNew)
            
    return lista_drones, lista_invernaderos