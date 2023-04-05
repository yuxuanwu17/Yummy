function fetchOrderTotalPrice() {
    $.ajax({
        url: '/yummy/get_order_total_price',
        method: 'GET',
        success: function (response) {
            if (response.success) {
                $("#total-price-counter").html("Total price: $" + response.total_price.toFixed(2) + "<br>Click Here Check Out");


                // Initialize itemCounts and totalCount with values from the server
                response.food_quantities.forEach(function (item) {
                    itemCounts[item.food_id] = item.quantity;
                    totalCount += item.quantity;
                    updateQuantityDisplay(item.food_id, item.quantity); // Add this line
                });

                // Update the total count counter button
                $("#total-price-counter").html("Total price: $" + response.total_price.toFixed(2) + "<br>Click Here Check Out");
            } else {
                console.log("An error occurred while fetching the order's total price");
            }
        },
        error: function (response) {
            console.log("An error occurred while fetching the order's total price");
        }
    });
}

// Update the quantity-display element for the specified itemId
function updateQuantityDisplay(itemId, quantity) {
    $('.quantity-display[data-item="' + itemId + '"]').text(quantity);
}