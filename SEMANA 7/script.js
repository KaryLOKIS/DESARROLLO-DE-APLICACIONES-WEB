// ===== ARREGLO DE PRODUCTOS =====
const productos = [
  {
    nombre: "Laptop",
    precio: 750,
    descripcion: "Equipo portátil para estudios"
  },
  {
    nombre: "Celular",
    precio: 300,
    descripcion: "Teléfono inteligente"
  },
  {
    nombre: "Audífonos",
    precio: 25,
    descripcion: "Audífonos inalámbricos"
  }
];

// ===== ACCESO AL DOM =====
const lista = document.getElementById("listaProductos");
const btnAgregar = document.getElementById("btnAgregar");

// ===== FUNCIÓN DE RENDERIZADO PLANTILLA =====
function renderizarProductos() {
  lista.innerHTML = "";

  productos.forEach((producto) => {
    // plantilla básica usando template string
    const item = document.createElement("li");
    item.innerHTML = `
      <strong>${producto.nombre}</strong><br>
      Precio: $${producto.precio}<br>
      ${producto.descripcion}
    `;
    lista.appendChild(item);
  });
}

// ===== RENDERIZAR AL CARGAR =====
renderizarProductos();

// ===== BOTÓN AGREGAR =====
btnAgregar.addEventListener("click", () => {

  const nuevoProducto = {
    nombre: "Producto nuevo",
    precio: 10,
    descripcion: "Descripción del producto"
  };

  productos.push(nuevoProducto);  // agregar al arreglo
  renderizarProductos();          // volver a renderizar lista
});
