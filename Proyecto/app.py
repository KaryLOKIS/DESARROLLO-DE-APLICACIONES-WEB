from flask import Flask

app = Flask(__name__)

# Ruta principal
@app.route("/")
def inicio():
    return "Bienvenido a Mundo Mascotas  - Tu tienda online de accesorios, ropa y comida para mascotas"

# Ruta de productos
@app.route("/productos")
def productos():
    return "Categorías disponibles: Comida , Ropa , Accesorios , Juguetes "

# Ruta dinámica para productos
@app.route("/producto/<nombre>")
def producto(nombre):
    return f"Producto: {nombre} – disponible en Mundo Mascotas "

# Ruta dinámica para clientes (opcional pero suma puntos)
@app.route("/cliente/<nombre>")
def cliente(nombre):
    return f"Bienvenido, {nombre}. Gracias por visitar Mundo Mascotas "

if __name__ == "__main__":
    app.run(debug=True)
