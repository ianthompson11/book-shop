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
                          // 3. Limpiar COMPLETAMENTE el carrito después de confirmar que se guardó la orden
                          console.log("🧹 Iniciando limpieza completa del carrito...");
                          
                          // Limpiar TODAS las claves de localStorage relacionadas con el carrito
                          const cartKeys = ['cart', 'cart_selected', 'cart_checkout', 'cartCount', 'cartItems', 'shopping_cart', 'user_cart'];
                          cartKeys.forEach(key => {
                              if (localStorage.getItem(key)) {
                                  console.log(`Removiendo ${key}:`, localStorage.getItem(key));
                                  localStorage.removeItem(key);
                              }
                          });
                          
                          // Establecer contador en 0
                          localStorage.setItem("cartCount", "0");
                          
                          // Actualizar TODOS los elementos posibles del contador en la UI
                          const selectors = [
                              '#cart-count', '.cart-count', '[data-cart-count]',
                              '#cartCount', '.cartCount', '#cart_count', '.cart_count',
                              '.badge', '.counter', '[class*="count"]', '[id*="count"]',
                              'a[href*="cart"] span', 'a[href*="carrito"] span'
                          ];
                          
                          let updated = false;
                          selectors.forEach(selector => {
                              const elements = document.querySelectorAll(selector);
                              elements.forEach(elem => {
                                  if (elem.textContent && (elem.textContent.includes('(') || /\d+/.test(elem.textContent))) {
                                      console.log(`Actualizando elemento: ${selector} -> "${elem.textContent}" a "(0)"`);
                                      elem.textContent = elem.textContent.replace(/\(\d+\)/, '(0)').replace(/^\d+$/, '0');
                                      if (elem.textContent.includes('(') && !elem.textContent.includes('(0)')) {
                                          elem.textContent = '(0)';
                                      }
                                      updated = true;
                                  }
                              });
                          });
                          
                          // También disparar un evento personalizado para que otros scripts puedan reaccionar
                          window.dispatchEvent(new CustomEvent('cartCleared', { detail: { success: true } }));
                          
                          // Si existe updateCartCount como función global, llamarla
                          if (typeof window.updateCartCount === 'function') {
                              window.updateCartCount(0);
                          }
                          
                          console.log(`✅ Carrito completamente limpiado. UI actualizada: ${updated}`);
                          console.log("✅ Orden guardada exitosamente:", result);
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

