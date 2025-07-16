// Inicializa el carrito desde localStorage o lo crea si no existe
let cart = JSON.parse(localStorage.getItem("cart")) || [];


/**
 * Función para agregar productos al carrito
 * Ya no requiere autenticación para agregar productos
 */
function addToCart(name, price, description, id) {
    // Verifica si el producto ya está en el carrito usando el id
    const existingItem = cart.find(item => item.id === id);
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({ name, quantity: 1, price, description, id });
    }

    localStorage.setItem('cart', JSON.stringify(cart));
    alert("Producto agregado al carrito");

    // Actualiza contador del navbar (si está presente)
    const cartCount = document.getElementById("cart-count");
    if (cartCount) {
        cartCount.textContent = `(${cart.length})`;
    }
}

    // Actualiza contador del navbar (si está presente)
    const cartCount = document.getElementById("cart-count");
    if (cartCount) {
        cartCount.textContent = `(${cart.length})`;
    }
}


