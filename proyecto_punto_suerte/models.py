class Producto:

    def __init__(self, id, nombre, cantidad, precio):
        self.id = id
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio

    def obtener_datos(self):
        return (self.id, self.nombre, self.cantidad, self.precio)


class Inventario:

    def __init__(self):
        self.productos = {}  # diccionario

    def agregar_producto(self, producto):
        self.productos[producto.id] = producto

    def eliminar_producto(self, id):
        if id in self.productos:
            del self.productos[id]

    def buscar_producto(self, nombre):
        for producto in self.productos.values():
            if producto.nombre == nombre:
                return producto

    def mostrar_productos(self):
        return list(self.productos.values())