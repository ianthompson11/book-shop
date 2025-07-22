const paypalButtons = window.paypal.Buttons({
   style: {
        shape: "rect",
        layout: "vertical",
        color: "gold",
        label: "paypal",
    },
   message: {
        amount: 100,
    },
   async createOrder() {
        try {
            // Primero intenta obtener el carrito de checkout, luego el carrito normal
            const cart = JSON.parse(localStorage.getItem("cart_checkout")) || 
                         JSON.parse(localStorage.getItem("cart_selected")) ||
                         JSON.parse(localStorage.getItem("cart")) || [];
            
            console.log("DEBUG - Carrito para PayPal:", cart); // Debug
            
            const response = await fetch("/api/orders/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                // use the "body" param to optionally pass additional order information
                // like product ids and quantities
                body: JSON.stringify({ cart }),

            });

            const orderData = await response.json();

            if (orderData.id) {
                return orderData.id;
            }
            const errorDetail = orderData?.details?.[0];
            const errorMessage = errorDetail
                ? `${errorDetail.issue} ${errorDetail.description} (${orderData.debug_id})`
                : JSON.stringify(orderData);

            throw new Error(errorMessage);
        } catch (error) {
            console.error(error);
            // resultMessage(`Could not initiate PayPal Checkout...<br><br>${error}`);
        }
    },
   async onApprove(data, actions) {
        try {
            const response = await fetch(
                `/api/orders/${data.orderID}/capture/`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                }
            );

            const orderData = await response.json();
            // Three cases to handle:
            //   (1) Recoverable INSTRUMENT_DECLINED -> call actions.restart()
            //   (2) Other non-recoverable errors -> Show a failure message
            //   (3) Successful transaction -> Show confirmation or thank you message

            const errorDetail = orderData?.details?.[0];

            if (errorDetail?.issue === "INSTRUMENT_DECLINED") {
                // (1) Recoverable INSTRUMENT_DECLINED -> call actions.restart()
                // recoverable state, per
                // https://developer.paypal.com/docs/checkout/standard/customize/handle-funding-failures/
                return actions.restart();
            } else if (errorDetail) {
                // (2) Other non-recoverable errors -> Show a failure message
                throw new Error(
                    `${errorDetail.description} (${orderData.debug_id})`
                );
            } else if (!orderData.purchase_units) {
                throw new Error(JSON.stringify(orderData));
            } else {
                // (3) Successful transaction -> Show confirmation or thank you message
                // Or go to another URL:  actions.redirect('thank_you.html');
                const transaction =
                    orderData?.purchase_units?.[0]?.payments?.captures?.[0] ||
                    orderData?.purchase_units?.[0]?.payments
                        ?.authorizations?.[0];
                        
                // Obtener el carrito antes de limpiarlo (usar el mismo carrito que se envió a PayPal)
                const cart = JSON.parse(localStorage.getItem("cart_checkout")) || 
                             JSON.parse(localStorage.getItem("cart_selected")) ||
                             JSON.parse(localStorage.getItem("cart")) || [];
                
                console.log("DEBUG - Carrito para confirmar compra:", cart); // Debug
                
                // 1. Guardar en localStorage que la compra fue confirmada
                localStorage.setItem("compraConfirmada", "true");

                // 2. Enviar la información del carrito a Django para crear la orden
                fetch("/api/marcar-compra/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        compraConfirmada: true,
                        transaction_id: transaction.id,
                        status: transaction.status,
                        cart: cart  // Enviar el carrito completo
                    }),
                }).then(response => response.json())
                  .then(result => {
                      console.log("Respuesta del servidor:", result);
                      if (result.success) {
                          // 3. Limpiar TODOS los tipos de carrito después de confirmar que se guardó la orden
                          console.log("Limpiando carrito después de compra exitosa...");
                          console.log("Estado ANTES del vaciado:");
                          console.log("cart:", localStorage.getItem("cart"));
                          console.log("cart_selected:", localStorage.getItem("cart_selected"));
                          console.log("cart_checkout:", localStorage.getItem("cart_checkout"));
                          console.log("cartCount:", localStorage.getItem("cartCount"));
                          
                          localStorage.removeItem("cart");
                          localStorage.removeItem("cart_selected");
                          localStorage.removeItem("cart_checkout");
                          localStorage.setItem("cartCount", "0");
                          
                          console.log("Estado DESPUÉS del vaciado:");
                          console.log("cart:", localStorage.getItem("cart"));
                          console.log("cart_selected:", localStorage.getItem("cart_selected"));
                          console.log("cart_checkout:", localStorage.getItem("cart_checkout"));
                          console.log("cartCount:", localStorage.getItem("cartCount"));
                          
                          // Actualizar el contador del carrito en la UI si existe
                          const cartCountElement = document.querySelector("#cart-count");
                          if (cartCountElement) {
                              cartCountElement.textContent = "(0)";
                              console.log("🔄 Contador UI actualizado a (0)");
                          } else {
                              console.log("⚠️ No se encontró el elemento #cart-count");
                          }
                          
                          // También buscar otras posibles formas del contador
                          const alternativeCounters = document.querySelectorAll('[class*="cart"], [id*="cart"], [class*="count"], [id*="count"]');
                          console.log("🔍 Elementos de carrito encontrados:", alternativeCounters.length);
                          alternativeCounters.forEach((elem, index) => {
                              console.log(`Elemento ${index}:`, elem.tagName, elem.className, elem.id, elem.textContent);
                              if (elem.textContent && elem.textContent.includes("(")) {
                                  elem.textContent = elem.textContent.replace(/\(\d+\)/, "(0)");
                                  console.log(`🔄 Actualizado elemento ${index}`);
                              }
                          });
                          
                          console.log("✅ Carrito limpiado exitosamente");
                          console.log("Orden guardada exitosamente:", result);
                      } else {
                          console.error("❌ Error al guardar la orden:", result.error);
                      }
                  })
                  .catch(error => {
                      console.error("Error en la comunicación con el servidor:", error);
                  });
                
                // Redirigir a la página de éxito
                window.location.href = `/order-success/?transaction_id=${transaction.id}&status=${transaction.status}`;
                console.log(
                    "Capture result",
                    orderData,
                    JSON.stringify(orderData, null, 2)
                );
            }
        } catch (error) {
            console.error(error);
            resultMessage(
                `Sorry, your transaction could not be processed...<br><br>${error}`
            );
        }
    },

   
});
paypalButtons.render("#paypal-button-container");


// Example function to show a result to the user. Your site's UI library can be used instead.
function resultMessage(message) {
    const container = document.querySelector("#result-message");
    container.innerHTML = message;
}

