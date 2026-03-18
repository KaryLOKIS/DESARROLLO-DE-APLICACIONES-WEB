from flask import Flask, render_template, request, redirect
import os

import json

from database import crear_tabla, conectar

app = Flask(__name__)

crear_tabla()

# Página principal
@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/inventario")
def inventario():

    buscar = request.args.get("buscar")

    conn = conectar()
    cursor = conn.cursor()

    if buscar:
        cursor.execute(
            "SELECT * FROM productos WHERE nombre LIKE ?",
            ('%' + buscar + '%',)
        )
    else:
        cursor.execute("SELECT * FROM productos")

    productos = cursor.fetchall()

    conn.close()

    return render_template("inventario.html", productos=productos)

@app.route("/agregar_producto", methods=["GET", "POST"])
def agregar_producto():

    if request.method == "POST":
        print("ENTRÓ AL POST")
        
        nombre = request.form["nombre"]
        cantidad = request.form["cantidad"]
        precio = request.form["precio"]

        print("🔥 GUARDANDO PRODUCTO...")  # 👈 para probar

        # ✅ TXT
        with open("inventario/data/datos.txt", "a") as archivo:
            archivo.write(f"{nombre},{cantidad},{precio}\n")

        # ✅ JSON
        ruta_json = "inventario/data/datos.json"

        try:
            with open(ruta_json, "r") as archivo:
                datos = json.load(archivo)
        except:
            datos = []

        nuevo_producto = {
            "nombre": nombre,
            "cantidad": cantidad,
            "precio": precio
        }

        datos.append(nuevo_producto)

        with open(ruta_json, "w") as archivo:
            json.dump(datos, archivo, indent=4)

        # ✅ SQLITE
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)",
            (nombre, cantidad, precio)
        )

        conn.commit()
        conn.close()

        return redirect("/inventario")

    return render_template("agregar_producto.html")

@app.route("/eliminar_producto/<int:id>")
def eliminar_producto(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM productos WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect("/inventario") 

@app.route("/editar_producto/<int:id>", methods=["GET", "POST"])
def editar_producto(id):

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":

        nombre = request.form["nombre"]
        cantidad = request.form["cantidad"]
        precio = request.form["precio"]

        cursor.execute(
            "UPDATE productos SET nombre=?, cantidad=?, precio=? WHERE id=?",
            (nombre, cantidad, precio, id)
        )

        conn.commit()
        conn.close()

        return redirect("/inventario")

    cursor.execute("SELECT * FROM productos WHERE id=?", (id,))
    producto = cursor.fetchone()

    conn.close()

    return render_template("editar_producto.html", producto=producto)       

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