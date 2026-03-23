from flask import Flask, render_template, request, redirect
import os
import csv
import json

from conexion.conexion import conectar

app = Flask(__name__)

# Página principal
@app.route("/")
def inicio():
    return render_template("index.html")


# INVENTARIO (LEER)
@app.route("/inventario")
def inventario():

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    buscar = request.args.get("buscar")

    if buscar:
        cursor.execute(
            "SELECT * FROM productos WHERE nombre LIKE %s",
            (f"%{buscar}%",)
        )
    else:
        cursor.execute("SELECT * FROM productos")

    productos = cursor.fetchall()

    conn.close()

    return render_template("inventario.html", productos=productos)


# AGREGAR PRODUCTO
@app.route("/agregar_producto", methods=["GET", "POST"])
def agregar_producto():

    if request.method == "POST":
        nombre = request.form["nombre"]
        cantidad = request.form["cantidad"]
        precio = request.form["precio"]

        # TXT
        with open("inventario/data/datos.txt", "a") as archivo:
            archivo.write(f"{nombre},{cantidad},{precio}\n")

        # CSV
        with open("inventario/data/datos.csv", "a", newline="") as archivo:
            writer = csv.writer(archivo)
            writer.writerow([nombre, cantidad, precio])

        # JSON
        ruta_json = "inventario/data/datos.json"

        try:
            with open(ruta_json, "r") as archivo:
                datos = json.load(archivo)
        except:
            datos = []

        nuevo_producto_json = {
            "nombre": nombre,
            "cantidad": cantidad,
            "precio": precio
        }

        datos.append(nuevo_producto_json)

        with open(ruta_json, "w") as archivo:
            json.dump(datos, archivo, indent=4)

        # MYSQL
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO productos (nombre, cantidad, precio) VALUES (%s, %s, %s)",
            (nombre, cantidad, precio)
        )

        conn.commit()
        conn.close()

        return redirect("/inventario")

    return render_template("agregar_producto.html")


# ELIMINAR
@app.route("/eliminar_producto/<int:id>")
def eliminar_producto(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM productos WHERE id = %s", (id,))

    conn.commit()
    conn.close()

    return redirect("/inventario")


# EDITAR
@app.route("/editar_producto/<int:id>", methods=["GET", "POST"])
def editar_producto(id):

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        nombre = request.form["nombre"]
        cantidad = request.form["cantidad"]
        precio = request.form["precio"]

        cursor.execute(
            "UPDATE productos SET nombre=%s, cantidad=%s, precio=%s WHERE id=%s",
            (nombre, cantidad, precio, id)
        )

        conn.commit()
        conn.close()

        return redirect("/inventario")

    cursor.execute("SELECT * FROM productos WHERE id=%s", (id,))
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


# Ruta dinámica
@app.route("/producto/<nombre>")
def producto(nombre):
    return render_template("producto_individual.html", nombre=nombre)


# VER DATOS (TXT, JSON, CSV)
@app.route("/datos")
def ver_datos():

    # TXT
    with open("inventario/data/datos.txt", "r") as archivo:
        datos_txt = archivo.readlines()

    # JSON
    try:
        with open("inventario/data/datos.json", "r") as archivo:
            datos_json = json.load(archivo)
    except:
        datos_json = []

    # CSV
    datos_csv = []
    with open("inventario/data/datos.csv", "r") as archivo:
        reader = csv.reader(archivo)
        for fila in reader:
            datos_csv.append(fila)

    return render_template(
        "datos.html",
        datos_txt=datos_txt,
        datos_json=datos_json,
        datos_csv=datos_csv
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)