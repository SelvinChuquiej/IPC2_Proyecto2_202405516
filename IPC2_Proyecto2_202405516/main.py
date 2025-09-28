from flask import Flask, render_template, current_app, redirect, url_for
from controlller.cargar_controller import cargar_bp

app = Flask(__name__)
app.secret_key = '202405516'

app.register_blueprint(cargar_bp)

@app.route('/')
def index():
    data = getattr(current_app, 'DATA', {
        'invernaderos': None,
        'planes': None,
        'archivo_actual': None
    })
    invernaderos = list(data['invernaderos']) if data['invernaderos'] else []
    planes = list(data['planes']) if data['planes'] else []
    archivo_actual = data.get('archivo_actual', None)
    return render_template('index.html', invernaderos=invernaderos, planes=planes, archivo_actual=archivo_actual)

@app.route('/limpiar', methods=['POST'])
def limpiar():
    if hasattr(current_app, 'DATA'):
        del current_app.DATA
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)