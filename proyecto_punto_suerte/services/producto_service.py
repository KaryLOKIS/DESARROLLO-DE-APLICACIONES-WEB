from conexion.conexion import conectar

# OBTENER PRODUCTOS
def obtener_productos(buscar=None):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    if buscar:
        cursor.execute(
            "SELECT * FROM productos WHERE nombre LIKE %s",
            (f"%{buscar}%",)
        )
    else:
        cursor.execute("SELECT * FROM productos")

    productos = cursor.fetchall()
    conn.close()

    return productos


# AGREGAR PRODUCTO
def agregar_producto(nombre, cantidad, precio):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO productos (nombre, cantidad, precio) VALUES (%s, %s, %s)",
        (nombre, cantidad, precio)
    )

    conn.commit()
    conn.close()


# ELIMINAR PRODUCTO ✅ CORREGIDO
def eliminar_producto(id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM productos WHERE id = %s", (id,))

    conn.commit()
    conn.close()


# OBTENER PRODUCTO POR ID ✅ CORREGIDO
def obtener_producto_por_id(id):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
    producto = cursor.fetchone()

    conn.close()

    return producto


# ACTUALIZAR PRODUCTO ✅ CORREGIDO
def actualizar_producto(id, nombre, cantidad, precio):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE productos SET nombre=%s, cantidad=%s, precio=%s WHERE id=%s",
        (nombre, cantidad, precio, id)
    )

    conn.commit()
    conn.close()