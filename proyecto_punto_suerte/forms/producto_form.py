class ProductoForm:
    def __init__(self, form):
        self.nombre = form.get("nombre")
        self.cantidad = form.get("cantidad")
        self.precio = form.get("precio")

    def es_valido(self):
        if not self.nombre or not self.cantidad or not self.precio:
            return False
        return True