// Leer el carrito desde localStorage
const cart = JSON.parse(localStorage.getItem("cart")) || [];

// Función para mostrar los productos en la lista
function displayCartItems() {
  const cartList = document.getElementById("cart-list");
  cartList.innerHTML = ""; // limpiar antes

  cart.forEach(product => {
    const li = document.createElement("li");
    li.textContent = `${product.quantity} x ${product.name} - $${product.price.toFixed(2)} (${product.description})`;
    cartList.appendChild(li);
  });
}

// Evento para guardar carrito y redirigir
document.getElementById("save-cart-btn").addEventListener("click", () => {
  // No necesitas guardar si ya está en localStorage, pero puedes actualizarlo si lo has modificado
  localStorage.setItem("cart", JSON.stringify(cart));
  window.location.href = "/payments/";
});

// Mostrar los productos al cargar la página
displayCartItems();

