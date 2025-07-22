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

    // Actualiza contador del navbar
    updateCartCounter();
}

/**
 * Función para actualizar el contador del carrito
 */
function updateCartCounter() {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const cartCount = document.getElementById("cart-count");
    if (cartCount) {
        cartCount.textContent = `(${cart.length})`;
    }
}

/**
 * Función para limpiar completamente el carrito
 */
function clearCart() {
    // Limpiar todas las variaciones de carrito en localStorage
    const cartKeys = ['cart', 'cart_selected', 'cart_checkout', 'cartCount', 'cartItems'];
    cartKeys.forEach(key => localStorage.removeItem(key));
    localStorage.setItem("cartCount", "0");
    
    // Actualizar variable global
    cart = [];
    
    // Actualizar contador UI
    updateCartCounter();
    
    console.log('🧹 Carrito limpiado desde cart.js');
}

// Inicializar carrito desde localStorage
let cart = JSON.parse(localStorage.getItem('cart')) || [];

// Actualizar contador al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    updateCartCounter();
});

// Escuchar evento de carrito limpio desde el sistema de pagos
window.addEventListener('cartCleared', function() {
    console.log('🎯 Evento cartCleared recibido en cart.js');
    clearCart();
});

// Hacer la función disponible globalmente
window.updateCartCount = function(count) {
    const cartCount = document.getElementById("cart-count");
    if (cartCount) {
        cartCount.textContent = `(${count || 0})`;
    }
};
