from flask import Flask, render_template

print("ESTE ES MI APP CORRECTO")

app = Flask(__name__)

# Página principal
@app.route("/")
def inicio():
    return render_template("index.html")

# Página acerca de
@app.route("/about/")
def about():
    return render_template("about.html")

# Página productos
@app.route("/productos/")
def productos():
    lista_productos = ["Collar", "Comida Premium", "Ropa para perro", "Juguete"]
    return render_template("productos.html", productos=lista_productos)

# Ruta dinámica
@app.route("/producto/<nombre>/")
def producto(nombre):
    return f"Producto: {nombre} – disponible en Mundo Mascotas 🐾"

print(app.url_map)   # ✅ AQUÍ AL FINAL

if __name__ == "__main__":
    app.run(debug=True)