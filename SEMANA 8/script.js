// Botón de alerta
document.getElementById("btnAlerta").addEventListener("click", () => {
  alert("¡Hola! Esta es una alerta personalizada ");
});

// Validación de formulario
const form = document.getElementById("contactoForm");

form.addEventListener("submit", function (e) {
  e.preventDefault();

  const nombre = document.getElementById("nombre");
  const correo = document.getElementById("correo");
  const mensaje = document.getElementById("mensaje");

  let valido = true;

  document.getElementById("errorNombre").textContent = "";
  document.getElementById("errorCorreo").textContent = "";
  document.getElementById("errorMensaje").textContent = "";
  document.getElementById("msgExito").textContent = "";

  if (nombre.value.trim() === "") {
    document.getElementById("errorNombre").textContent = "Nombre obligatorio";
    valido = false;
  }

  if (correo.value.trim() === "") {
    document.getElementById("errorCorreo").textContent = "Correo obligatorio";
    valido = false;
  }

  if (mensaje.value.trim() === "") {
    document.getElementById("errorMensaje").textContent = "Mensaje obligatorio";
    valido = false;
  }

  if (valido) {
    document.getElementById("msgExito").textContent =
      "Formulario enviado correctamente ";
    form.reset();
  }
});
