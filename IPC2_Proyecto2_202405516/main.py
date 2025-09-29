from flask import Flask, render_template, current_app, redirect, url_for
from controller.cargar_controller import cargar_bp
from controller.simulacion_controller import simulacion_bp

app = Flask(__name__)
app.secret_key = '202405516'

app.register_blueprint(cargar_bp)
app.register_blueprint(simulacion_bp)

if __name__ == '__main__':
	app.run(debug=True)