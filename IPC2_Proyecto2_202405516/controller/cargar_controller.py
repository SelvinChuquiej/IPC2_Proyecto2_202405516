from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from controller.xml_reader import leer_archivo
from models.ListaEnlazada import ListaEnlazada
import io

cargar_bp = Blueprint('cargar', __name__)

class AppData:
    __slots__ = (
        'drones',
        'invernaderos',
        'planes',
        'drones_objetos',
        'invernaderos_objetos',
        'archivo_actual'
    )

    def __init__(self):
        self.drones = None                 # ListaEnlazada para mostrar
        self.invernaderos = None           # ListaEnlazada para mostrar
        self.planes = None                 # ListaEnlazada para mostrar
        self.drones_objetos = None         # ListaEnlazada para simulación
        self.invernaderos_objetos = None   # ListaEnlazada para simulación
        self.archivo_actual = None         # str o None

def get_data():
    if not hasattr(current_app, 'DATA'):
        current_app.DATA = AppData()
    return current_app.DATA

@cargar_bp.route('/')
def index():
    data = getattr(current_app, 'DATA', None)
    if data is None:
        data = get_data()

    return render_template( 'index.html', invernaderos=data.invernaderos, planes=data.planes, archivo_actual=data.archivo_actual )

@cargar_bp.route('/cargar', methods=['POST'])
def cargar_xml():
    archivo = request.files.get('archivo_xml')
    if not archivo or not archivo.filename.lower().endswith('.xml'):
        flash('Por favor selecciona un archivo XML válido', 'danger')
        return redirect(url_for('cargar.index'))

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
        data.invernaderos = nombres_invernaderos
        data.planes = nombres_planes
        data.invernaderos_objetos = lista_invernaderos
        data.drones_objetos = lista_drones
        data.archivo_actual = archivo.filename

        flash('Archivo cargado correctamente', 'success')
        return redirect(url_for('cargar.index'))

    except Exception as e:
        flash(f'Error al procesar el archivo XML: {e}', 'danger')
        return redirect(url_for('cargar.index'))


@cargar_bp.route('/limpiar', methods=['POST'])
def limpiar():
    if hasattr(current_app, 'DATA'):
        delattr(current_app, 'DATA')
    return redirect(url_for('cargar.index'))
