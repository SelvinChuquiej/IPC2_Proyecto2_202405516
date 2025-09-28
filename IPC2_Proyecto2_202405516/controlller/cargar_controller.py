from flask import Blueprint, request, redirect, url_for, flash, current_app
from controlller.xml_reader import leer_archivo
from models.ListaEnlazada import ListaEnlazada
import io

cargar_bp = Blueprint('cargar', __name__)

def get_data():
    if not hasattr(current_app, 'DATA'):
        current_app.DATA = {
            'drones': None,                 # ListaEnlazada para mostrar
            'invernaderos': None,           # ListaEnlazada para mostrar
            'planes': None,                 # ListaEnlazada para mostrar
            'drones_objetos': None,         # ListaEnlazada para simulación
            'invernaderos_objetos': None    # ListaEnlazada para simulación
        }
    return current_app.DATA

@cargar_bp.route('/cargar', methods=['POST'])
def cargar_xml():
    archivo = request.files.get('archivo_xml')
    if not archivo or not archivo.filename.lower().endswith('.xml'):
        flash('Por favor selecciona un archivo XML válido', 'danger')
        return redirect(url_for('index'))
    try:
        contenido = archivo.read()
        lista_drones, lista_invernaderos = leer_archivo(io.BytesIO(contenido))
        nombres_invernaderos = ListaEnlazada()
        nombres_planes = ListaEnlazada()

        for inv in lista_invernaderos:
            nombres_invernaderos.insertar(inv.nombre)
            for plan in inv.planes_riego:
                nombres_planes.insertar(plan.nombre)

        data = get_data()
        data['invernaderos'] = nombres_invernaderos
        data['planes'] = nombres_planes
        data['invernaderos_objetos'] = lista_invernaderos
        data['drones_objetos'] = lista_drones
        data['archivo_actual'] = archivo.filename  # Guardar nombre del archivo
        flash('Archivo cargado correctamente', 'success')
        return redirect(url_for('index'))
    
    except Exception as e:
        flash(f'Error al procesar el archivo XML: {e}', 'danger')
        return redirect(url_for('index'))
