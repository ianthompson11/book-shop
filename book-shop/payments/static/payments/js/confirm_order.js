const cart = [
  { name: "Zapatos Rojos", quantity: 1, price: 50.0, description: "Zapatos deportivos", sku: "zapatos-rojos-01" },
  { name: "Gorra Negra", quantity: 2, price: 20.0, description: "Gorra clásica", sku: "gorra-negra-02" },
  { name: "Jeans Azules", quantity: 1, price: 50.0, description: "Jeans clásicos", sku: "jeans-azul-03" },
];

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
  localStorage.setItem("cart", JSON.stringify(cart));
  window.location.href = "/payments/";
});

// Mostrar los productos al cargar la página
displayCartItems();
