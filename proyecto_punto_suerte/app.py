from flask import Flask, render_template, request, redirect
import os
import csv
import json

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from flask import make_response

# SERVICES
from services.producto_service import (
    obtener_productos,
    agregar_producto as agregar_producto_db,
    eliminar_producto as eliminar_producto_db,
    obtener_producto_por_id,
    actualizar_producto
)

# FORMS (opcional pero suma puntos)
from forms.producto_form import ProductoForm

# LOGIN
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from conexion.conexion import conectar

app = Flask(__name__)
app.secret_key = "clave_secreta"


# ---------------- LOGIN ----------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class Usuario(UserMixin):
    def __init__(self, id, nombre, email, password):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password = password


@login_manager.user_loader
def load_user(user_id):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return Usuario(
            user["id_usuario"],
            user["nombre"],
            user["email"],
            user["password"]
        )
    return None


# ------------------ INICIO ------------------
@app.route("/")
def inicio():
    return render_template("index.html")


# ------------------ LOGIN ------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = conectar()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):

            usuario = Usuario(
                user["id_usuario"],
                user["nombre"],
                user["email"],
                user["password"]
            )

            login_user(usuario)
            return redirect("/inventario")

        else:
            return "❌ Usuario o contraseña incorrectos"

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


# ---------------- REGISTRO ----------------

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":

        nombre = request.form["nombre"]
        email = request.form["email"]
        password = request.form["password"]

        password_cifrado = generate_password_hash(password)

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)",
            (nombre, email, password_cifrado)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("registro.html")


# ------------------ PRODUCTOS ------------------

@app.route("/inventario")
@login_required
def inventario():
    buscar = request.args.get("buscar")
    productos = obtener_productos(buscar)
    return render_template("inventario.html", productos=productos)


@app.route("/agregar_producto", methods=["GET", "POST"])
@login_required
def agregar_producto():

    if request.method == "POST":

        form = ProductoForm(request.form)

        if not form.es_valido():
            return "❌ Todos los campos son obligatorios"

        nombre = form.nombre
        cantidad = form.cantidad
        precio = form.precio

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

        datos.append({
            "nombre": nombre,
            "cantidad": cantidad,
            "precio": precio
        })

        with open(ruta_json, "w") as archivo:
            json.dump(datos, archivo, indent=4)

        # MYSQL
        agregar_producto_db(nombre, cantidad, precio)

        return redirect("/inventario")

    return render_template("agregar_producto.html")


@app.route("/eliminar_producto/<int:id>")
@login_required
def eliminar_producto(id):
    eliminar_producto_db(id)
    return redirect("/inventario")


@app.route("/editar_producto/<int:id>", methods=["GET", "POST"])
@login_required
def editar_producto(id):

    if request.method == "POST":

        form = ProductoForm(request.form)

        if not form.es_valido():
            return "❌ Todos los campos son obligatorios"

        actualizar_producto(
            id,
            form.nombre,
            form.cantidad,
            form.precio
        )

        return redirect("/inventario")

    producto = obtener_producto_por_id(id)
    return render_template("editar_producto.html", producto=producto)


# ------------------ USUARIOS ------------------

@app.route("/usuarios")
@login_required
def usuarios():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()

    conn.close()

    return render_template("usuarios.html", usuarios=usuarios)


# ------------------ OTROS ------------------

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/productos")
def productos():
    return render_template("productos.html")


@app.route("/producto/<nombre>")
def producto(nombre):
    return render_template("producto_individual.html", nombre=nombre)


@app.route("/datos")
def ver_datos():

    with open("inventario/data/datos.txt", "r") as archivo:
        datos_txt = archivo.readlines()

    try:
        with open("inventario/data/datos.json", "r") as archivo:
            datos_json = json.load(archivo)
    except:
        datos_json = []

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

@app.route("/reporte_pdf")
@login_required
def reporte_pdf():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT nombre, cantidad, precio FROM productos")
    datos = cursor.fetchall()
    conn.close()

    # Crear respuesta PDF
    response = make_response()
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=reporte.pdf'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elementos = []

    estilos = getSampleStyleSheet()

    # TÍTULO
    elementos.append(Paragraph("REPORTE DE PRODUCTOS - PUNTO DE LA SUERTE", estilos['Title']))
    elementos.append(Spacer(1, 20))

    # TABLA
    tabla_datos = [["Nombre", "Cantidad", "Precio", "Total"]]

    total_general = 0

    for fila in datos:
        nombre, cantidad, precio = fila
        total = cantidad * float(precio)
        total_general += total

        tabla_datos.append([nombre, cantidad, precio, round(total, 2)])

    tabla_datos.append(["", "", "TOTAL", round(total_general, 2)])

    tabla = Table(tabla_datos)

    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey)
    ]))

    elementos.append(tabla)

    doc.build(elementos)

    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)