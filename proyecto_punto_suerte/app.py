from flask import Flask, render_template, request, redirect
import os

import csv

import json

from database import crear_tabla, conectar

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from models import Producto

crear_tabla()

# Página principal
@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/inventario")
def inventario():

    buscar = request.args.get("buscar")

    if buscar:
        productos = Producto.query.filter(
            Producto.nombre.like(f"%{buscar}%")
        ).all()
    else:
        productos = Producto.query.all()

    return render_template("inventario.html", productos=productos)

@app.route("/agregar_producto", methods=["GET", "POST"])
def agregar_producto():

    if request.method == "POST":
        print("ENTRÓ AL POST")
        
        nombre = request.form["nombre"]
        cantidad = request.form["cantidad"]
        precio = request.form["precio"]

        print("🔥 GUARDANDO PRODUCTO...")  # 👈 para probar

        #  TXT
        with open("inventario/data/datos.txt", "a") as archivo:
            archivo.write(f"{nombre},{cantidad},{precio}\n")

        # GUARDAR EN CSV
        with open("inventario/data/datos.csv", "a", newline="") as archivo:
            writer = csv.writer(archivo)
            writer.writerow([nombre, cantidad, precio])    

        #  JSON
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

        nuevo = Producto(
            nombre=nombre,
            cantidad=cantidad,
            precio=precio
        )

        db.session.add(nuevo)
        db.session.commit()

        return redirect("/inventario")

    return render_template("agregar_producto.html")

@app.route("/eliminar_producto/<int:id>")
def eliminar_producto(id):

    producto = Producto.query.get(id)

    if producto:
        db.session.delete(producto)
        db.session.commit()

    return redirect("/inventario") 

@app.route("/editar_producto/<int:id>", methods=["GET", "POST"])
def editar_producto(id):

    producto = Producto.query.get(id)

    if request.method == "POST":

        producto.nombre = request.form["nombre"]
        producto.cantidad = request.form["cantidad"]
        producto.precio = request.form["precio"]

        db.session.commit()

        return redirect("/inventario")

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


@app.route("/datos")
def ver_datos():

    # TXT
    with open("inventario/data/datos.txt", "r") as archivo:
        datos_txt = archivo.readlines()

    # JSON
    import json
    try:
        with open("inventario/data/datos.json", "r") as archivo:
            datos_json = json.load(archivo)
    except:
        datos_json = []

    # CSV
    import csv
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

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)