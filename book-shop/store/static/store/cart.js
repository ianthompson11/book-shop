// Recuperar carrito existente o crear uno nuevo
let cart = JSON.parse(localStorage.getItem('cart')) || [];

// Función para agregar un producto al carrito
function addToCart(name, price, description, sku) {
    const existingItem = cart.find(item => item.sku === sku);
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({ name, quantity: 1, price, description, sku });
    }

    // Guardar el carrito actualizado en localStorage
    localStorage.setItem('cart', JSON.stringify(cart));
    alert("Producto agregado al carrito");
}

// Detectar clic en el botón "Confirmar Pedido"
document.addEventListener("DOMContentLoaded", () => {
    const confirmButton = document.getElementById("confirmar-carrito");
    if (confirmButton) {
        confirmButton.addEventListener("click", () => {
            window.location.href = "/confirm-order/";
        });
    }
});
