// Inicializa el carrito desde localStorage o lo crea si no existe
let cart = JSON.parse(localStorage.getItem("cart_selected")) || [];


/**
 * Función para agregar productos al carrito
 * Redirige a login si el usuario no está autenticado
 */
function addToCart(name, price, description, sku) {
    const isAuthenticated = document.body.getAttribute('data-authenticated') === "true";

    if (!isAuthenticated) {
        window.location.href = "/accounts/login/?next=/products/";
        return;
    }

    // Verifica si el producto ya está en el carrito
    const existingItem = cart.find(item => item.sku === sku);
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({ name, quantity: 1, price, description, sku });
    }

    localStorage.setItem('cart', JSON.stringify(cart));
    alert("Producto agregado al carrito");

    // Actualiza contador del navbar (si está presente)
    const cartCount = document.getElementById("cart-count");
    if (cartCount) {
        cartCount.textContent = `(${cart.length})`;
    }
}


