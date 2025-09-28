from flask import Flask, render_template, current_app
from controlller.cargar_controller import cargar_bp

app = Flask(__name__)
app.secret_key = '202405516'

app.register_blueprint(cargar_bp)

@app.route('/')
def index():
    data = getattr(current_app, 'DATA', {
        'invernaderos': None,
        'planes': None
    })
    invernaderos = data['invernaderos'] or []
    planes = data['planes'] or []
    return render_template('index.html', invernaderos=invernaderos, planes=planes)

if __name__ == '__main__':
    app.run(debug=True)