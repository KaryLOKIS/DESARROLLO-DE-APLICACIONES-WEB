from flask import Flask, render_template, request, redirect, make_response
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from io import BytesIO
from flask import make_response
import os
from io import BytesIO, StringIO
from datetime import datetime
import json
import csv
import random




# PDF
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

# SERVICES
from services.producto_service import (
    obtener_productos,
    agregar_producto as agregar_producto_db,
    eliminar_producto as eliminar_producto_db,
    obtener_producto_por_id,
    actualizar_producto
)

# FORMS
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
        return Usuario(user["id_usuario"], user["nombre"], user["email"], user["password"])
    return None

# ---------------- INICIO ----------------
@app.route("/")
def inicio():
    return render_template("index.html")

# ---------------- LOGIN ----------------
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
            usuario = Usuario(user["id_usuario"], user["nombre"], user["email"], user["password"])
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

# ---------------- USUARIOS ----------------
@app.route("/usuarios")
@login_required
def usuarios():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()

    conn.close()

    return render_template("usuarios.html", usuarios=usuarios)

# ---------------- LOTERÍA ----------------
@app.route("/loteria", methods=["GET", "POST"])
@login_required
def loteria():

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios")
    clientes = cursor.fetchall()

    if request.method == "POST":

        numero = request.form["numero"]
        cliente = request.form["cliente"]
        valor = request.form["valor"]

        cursor.execute(
            "INSERT INTO boletos (numero, id_usuario, fecha, valor) VALUES (%s, %s, NOW(), %s)",
            (numero, cliente, valor)
        )

        conn.commit()
        conn.close()

        return redirect("/loteria")

    cursor.execute("""
        SELECT b.*, u.nombre 
        FROM boletos b
        JOIN usuarios u ON b.id_usuario = u.id_usuario
        ORDER BY b.id_boleto DESC
    """)

    jugadas = cursor.fetchall()

    conn.close()

    return render_template("loteria.html", clientes=clientes, jugadas=jugadas)

@app.route("/sortear")
@login_required
def sortear():

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    numero_ganador = random.randint(0, 99)

    cursor.execute("""
        SELECT b.*, u.nombre 
        FROM boletos b
        JOIN usuarios u ON b.id_usuario = u.id_usuario
        WHERE b.numero = %s
    """, (numero_ganador,))

    ganadores = cursor.fetchall()

    conn.close()

    return render_template(
        "resultado.html",
        numero=numero_ganador,
        ganadores=ganadores
    )

# ---------------- EXPORTAR ----------------
@app.route("/exportar_json")
@login_required
def exportar_json():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    datos = cursor.fetchall()
    conn.close()

    response = make_response(json.dumps(datos, indent=4, default=str))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = 'attachment; filename=productos.json'
    return response

@app.route("/exportar_csv")
@login_required
def exportar_csv():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, cantidad, precio FROM productos")
    datos = cursor.fetchall()
    conn.close()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Nombre", "Cantidad", "Precio"])

    for fila in datos:
        writer.writerow(fila)

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=productos.csv"
    response.headers["Content-Type"] = "text/csv"
    return response

@app.route("/exportar_txt")
@login_required
def exportar_txt():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, cantidad, precio FROM productos")
    datos = cursor.fetchall()
    conn.close()

    contenido = ""
    for fila in datos:
        contenido += f"{fila[0]} | {fila[1]} | {fila[2]}\n"

    response = make_response(contenido)
    response.headers["Content-Disposition"] = "attachment; filename=productos.txt"
    response.headers["Content-Type"] = "text/plain"
    return response

# ---------------- INVENTARIO ----------------
@app.route("/inventario")
@login_required
def inventario():
    buscar = request.args.get("buscar")
    productos = obtener_productos(buscar)

    if productos is None:
        productos = []

    return render_template("inventario.html", productos=productos)

@app.route("/agregar_producto", methods=["GET", "POST"])
@login_required
def agregar_producto():

    if request.method == "POST":
        form = ProductoForm(request.form)

        if not form.es_valido():
            return "❌ Campos vacíos"

        agregar_producto_db(form.nombre, form.cantidad, form.precio)
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
            return "❌ Campos vacíos"

        actualizar_producto(id, form.nombre, form.cantidad, form.precio)
        return redirect("/inventario")

    producto = obtener_producto_por_id(id)
    return render_template("editar_producto.html", producto=producto)

@app.route("/facturar", methods=["GET", "POST"])
@login_required
def facturar():

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios")
    clientes = cursor.fetchall()

    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()

    if request.method == "POST":

        usuario_id = request.form["cliente"]
        producto_id = request.form["producto"]
        cantidad = int(request.form["cantidad"])

        # VALIDAR STOCK
        cursor.execute("SELECT cantidad FROM productos WHERE id=%s", (producto_id,))
        stock = cursor.fetchone()

        if stock["cantidad"] < cantidad:
            conn.close()
            return "No hay suficiente stock"

        # Obtener precio
        cursor.execute("SELECT precio FROM productos WHERE id=%s", (producto_id,))
        producto = cursor.fetchone()

        precio = float(producto["precio"])
        total = precio * cantidad

        # INSERTAR FACTURA
        cursor.execute(
            "INSERT INTO facturas (id_usuario, fecha, total) VALUES (%s, NOW(), %s)",
            (usuario_id, total)
        )

        id_factura = cursor.lastrowid

        # INSERTAR DETALLE
        cursor.execute(
            """INSERT INTO detalle_factura (id_factura, id_producto, cantidad, precio)
               VALUES (%s, %s, %s, %s)""",
            (id_factura, producto_id, cantidad, precio)
        )

        # DESCONTAR STOCK
        cursor.execute(
            "UPDATE productos SET cantidad = cantidad - %s WHERE id = %s",
            (cantidad, producto_id)
        )

        conn.commit()
        conn.close()

        return redirect(f"/factura/{id_factura}")

    conn.close()
    return render_template("facturar.html", clientes=clientes, productos=productos)

@app.route("/factura_pdf/<int:id>")
@login_required
def factura_pdf(id):

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT f.id_factura, f.fecha, f.total,
               u.nombre AS cliente,
               p.nombre AS producto,
               d.cantidad, d.precio
        FROM facturas f
        JOIN usuarios u ON f.id_usuario = u.id_usuario
        JOIN detalle_factura d ON d.id_factura = f.id_factura
        JOIN productos p ON d.id_producto = p.id
        WHERE f.id_factura = %s
    """, (id,))

    datos = cursor.fetchall()
    conn.close()

    # CREAR PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)

    elementos = []

    # TÍTULO
    elementos.append(Paragraph(f"Factura #{datos[0]['id_factura']}",))
    elementos.append(Spacer(1, 10))

    # TABLA
    data = [["Producto", "Cantidad", "Precio"]]

    for d in datos:
        data.append([d["producto"], d["cantidad"], d["precio"]])

    tabla = Table(data)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.green),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))

    elementos.append(tabla)
    elementos.append(Spacer(1, 10))

    # TOTAL
    elementos.append(Paragraph(f"Total: ${datos[0]['total']}",))

    doc.build(elementos)

    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=factura_{id}.pdf'

    return response


# ---------------- FACTURAS ----------------
@app.route("/facturas")
@login_required
def ver_facturas():

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT f.id_factura, u.nombre, f.fecha, f.total
        FROM facturas f
        JOIN usuarios u ON f.id_usuario = u.id_usuario
        ORDER BY f.id_factura DESC
    """)

    facturas = cursor.fetchall()

    if facturas is None:
        facturas = []

    conn.close()

    return render_template("facturas.html", facturas=facturas)

@app.route("/factura/<int:id>")
@login_required
def ver_factura(id):

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT f.id_factura, f.fecha, f.total,
               u.nombre AS cliente,
               p.nombre AS producto,
               d.cantidad, d.precio
        FROM facturas f
        JOIN usuarios u ON f.id_usuario = u.id_usuario
        JOIN detalle_factura d ON d.id_factura = f.id_factura
        JOIN productos p ON d.id_producto = p.id
        WHERE f.id_factura = %s
    """, (id,))

    datos = cursor.fetchall()

    conn.close()

    return render_template("ver_factura.html", datos=datos)



# ------------ Dashboard -----------------------    

@app.route("/dashboard")
@login_required
def dashboard():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT SUM(valor) as total FROM boletos")
    result = cursor.fetchone()
    total = result["total"] if result["total"] else 0

    cursor.execute("SELECT COUNT(*) as cantidad FROM boletos")
    cantidad = cursor.fetchone()["cantidad"]

    cursor.execute("SELECT numero FROM boletos ORDER BY id_boleto DESC LIMIT 1")
    ultimo = cursor.fetchone()
    ultimo = ultimo["numero"] if ultimo else 0

    conn.close()

    return render_template("dashboard.html", total=total, cantidad=cantidad, ultimo=ultimo)    

# ---------------- PDF ----------------
@app.route("/reporte_pdf")
@login_required
def reporte_pdf():

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, cantidad, precio FROM productos")
    datos = cursor.fetchall()
    conn.close()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elementos = []
    estilos = getSampleStyleSheet()

    elementos.append(Paragraph("PUNTO DE LA SUERTE", estilos['Title']))
    elementos.append(Paragraph("Sistema de Facturación", estilos['Normal']))
    elementos.append(Spacer(1, 10))

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    elementos.append(Paragraph(f"Fecha: {fecha}", estilos['Normal']))
    elementos.append(Spacer(1, 20))

    tabla_datos = [["Nombre", "Cantidad", "Precio", "Total"]]

    for fila in datos:
        total = fila[1] * float(fila[2])
        tabla_datos.append([fila[0], fila[1], fila[2], total])

    tabla = Table(tabla_datos)

    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elementos.append(tabla)
    doc.build(elementos)

    buffer.seek(0)

    return make_response(buffer.getvalue(), 200, {
        'Content-Type': 'application/pdf'
    })

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)