const imageUrlInput = document.getElementById("imageUrl");
const addImageBtn = document.getElementById("addImageBtn");
const deleteImageBtn = document.getElementById("deleteImageBtn");
const gallery = document.getElementById("gallery");

let selectedImage = null;


addImageBtn.addEventListener("click", () => {
    const imageUrl = imageUrlInput.value.trim();
    if (imageUrl === "") return;

    const img = document.createElement("img");
    img.src = imageUrl;

    
    img.addEventListener("click", () => {
        if (selectedImage) {
            selectedImage.classList.remove("selected");
        }
        img.classList.add("selected");
        selectedImage = img;
    });

    gallery.appendChild(img);
    imageUrlInput.value = "";
});


deleteImageBtn.addEventListener("click", () => {
    if (selectedImage) {
        selectedImage.remove();
        selectedImage = null;
    } else {
        alert("No hay ninguna imagen seleccionada");
    }
});


imageUrlInput.addEventListener("input", () => {
    console.log("URL ingresada:", imageUrlInput.value);
});


document.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        addImageBtn.click();
    }

    if (event.key === "Delete") {
        deleteImageBtn.click();
    }
});
