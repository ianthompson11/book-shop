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
            // Usar cart_checkout que contiene solo los productos seleccionados para la compra
            const cart = JSON.parse(localStorage.getItem("cart_checkout")) || [];
            
            if (cart.length === 0) {
                throw new Error("No hay productos seleccionados para la compra.");
            }
            
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
                // 1. Guardar en localStorage
                localStorage.setItem("compraConfirmada", "true");

                // 2. Enviar a Django y limpiar carrito si es exitoso
                fetch("/api/marcar-compra/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        compraConfirmada: true,
                        transaction_id: transaction.id,
                        status: transaction.status,
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.clear_cart) {
                        // Obtener el carrito principal y el carrito de compra
                        const mainCart = JSON.parse(localStorage.getItem("cart")) || [];
                        const purchasedCart = JSON.parse(localStorage.getItem("cart_checkout")) || [];
                        
                        // Remover los productos comprados del carrito principal
                        const updatedMainCart = mainCart.filter(mainItem => {
                            return !purchasedCart.some(purchasedItem => 
                                purchasedItem.sku === mainItem.sku
                            );
                        });
                        
                        // Actualizar el carrito principal sin los productos comprados
                        if (updatedMainCart.length > 0) {
                            localStorage.setItem("cart", JSON.stringify(updatedMainCart));
                        } else {
                            localStorage.removeItem("cart");
                        }
                        
                        // Limpiar los carritos temporales
                        localStorage.removeItem("cart_selected");
                        localStorage.removeItem("cart_checkout");
                        
                        console.log("Productos comprados removidos del carrito principal");
                    }
                })
                .catch(error => {
                    console.error("Error al marcar compra como completada:", error);
                    // En caso de error, limpiar todo el carrito como medida de seguridad
                    localStorage.removeItem("cart");
                    localStorage.removeItem("cart_selected");
                    localStorage.removeItem("cart_checkout");
                });
                
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

