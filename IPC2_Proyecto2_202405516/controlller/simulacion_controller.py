from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from controlller.xml_reader import leer_archivo
from models.ListaEnlazada import ListaEnlazada
import io

simulacion_bp = Blueprint('simulacion', __name__)

@simulacion_bp.route('/simular', methods=['POST']) 
def simular():
    return render_template('reportes.html')
