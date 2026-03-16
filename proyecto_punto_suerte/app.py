from flask import Flask, render_template
import os

from database import crear_tabla, conectar

app = Flask(__name__)

crear_tabla()

# Página principal
@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/inventario")
def inventario():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()

    conn.close()

    return render_template("inventario.html", productos=productos)

# Página Acerca de
@app.route("/about")
def about():
    return render_template("about.html")

# Página Productos
@app.route("/productos")
def productos():
    return render_template("productos.html")

# Ruta dinámica ejemplo (producto individual)
@app.route("/producto/<nombre>")
def producto(nombre):
    return render_template("producto_individual.html", nombre=nombre)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)