from flask import Flask

app = Flask(__name__)

# Página principal
@app.route('/')
def inicio():
    return "Bienvenido al Sistema Web Punto de la Suerte – Consulta de juegos de Lotería Nacional"

# Ruta dinámica para usuarios
@app.route('/usuario/<nombre>')
def usuario(nombre):
    return f'Bienvenido {nombre}, gracias por visitar el Punto de la Suerte.'

# Ruta dinámica para productos
@app.route('/producto/<juego>')
def producto(juego):
    return f'Juego disponible: {juego}. Puedes comprarlo en nuestro Punto de la Suerte.'

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)