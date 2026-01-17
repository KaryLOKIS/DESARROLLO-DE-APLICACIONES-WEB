// ACCESO AL DOM
const form = document.getElementById("registroForm");

const nombre = document.getElementById("nombre");
const email = document.getElementById("email");
const password = document.getElementById("password");
const confirmPassword = document.getElementById("confirmPassword");
const edad = document.getElementById("edad");

const btnEnviar = document.getElementById("btnEnviar");
const msgFinal = document.getElementById("msgFinal");

// ERRORES
const nombreError = document.getElementById("nombreError");
const emailError = document.getElementById("emailError");
const passwordError = document.getElementById("passwordError");
const confirmPasswordError = document.getElementById("confirmPasswordError");
const edadError = document.getElementById("edadError");

// FUNCIONES DE ESTADO
function marcarValido(input, error) {
  input.classList.remove("invalido");
  input.classList.add("valid");
  error.textContent = "";
}

function marcarInvalido(input, error, mensaje) {
  input.classList.remove("valid");
  input.classList.add("invalido");
  error.textContent = mensaje;
}

// VALIDACIONES

function validarNombre() {
  if (nombre.value.trim().length < 3) {
    marcarInvalido(nombre, nombreError, "Mínimo 3 caracteres");
    return false;
  }
  marcarValido(nombre, nombreError);
  return true;
}

function validarEmail() {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!regex.test(email.value.trim())) {
    marcarInvalido(email, emailError, "Correo no válido");
    return false;
  }
  marcarValido(email, emailError);
  return true;
}

function validarPassword() {
  const regex = /^(?=.*\d)(?=.*[!@#$%^&*]).{8,}$/;
  if (!regex.test(password.value)) {
    marcarInvalido(password, passwordError, "8 caracteres, número y símbolo");
    return false;
  }
  marcarValido(password, passwordError);
  return true;
}

function validarConfirmacion() {
  if (confirmPassword.value !== password.value || confirmPassword.value === "") {
    marcarInvalido(confirmPassword, confirmPasswordError, "No coinciden");
    return false;
  }
  marcarValido(confirmPassword, confirmPasswordError);
  return true;
}

function validarEdad() {
  if (edad.value === "" || edad.value < 18) {
    marcarInvalido(edad, edadError, "Debe ser mayor de 18");
    return false;
  }
  marcarValido(edad, edadError);
  return true;
}

// HABILITAR BOTÓN
function validarFormulario() {
  const ok =
    validarNombre() 
    validarEmail() 
    validarPassword() 
    validarConfirmacion() 
    validarEdad();

  btnEnviar.disabled = !ok;
}

// EVENTOS DINÁMICOS
nombre.addEventListener("input", validarFormulario);
email.addEventListener("input", validarFormulario);
password.addEventListener("input", () => {
  validarPassword();
  validarConfirmacion();
  validarFormulario();
});
confirmPassword.addEventListener("input", validarFormulario);
edad.addEventListener("input", validarFormulario);

// SUBMIT
form.addEventListener("submit", function (e) {
  e.preventDefault();

  if (!btnEnviar.disabled) {
    msgFinal.textContent = "Formulario enviado correctamente ";
    form.reset();
    btnEnviar.disabled = true;

    [nombre, email, password, confirmPassword, edad].forEach(i =>
      i.classList.remove("valid", "invalido")
    );
  }
});
