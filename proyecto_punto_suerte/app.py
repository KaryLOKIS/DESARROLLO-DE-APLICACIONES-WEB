from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def inicio():
    return "Bienvenido al sistema Punto de la Suerte - Lotería Nacional"

@app.route("/producto/<nombre>")
def producto(nombre):
    return f"Producto disponible: {nombre}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)