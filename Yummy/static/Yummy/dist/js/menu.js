function fetchOrderTotalPrice() {
    $.ajax({
        url: '/yummy/get_order_total_price',
        method: 'GET',
        success: function (response) {
            if (response.success) {
                $("#total-price-counter").text("Total price: $" + response.total_price.toFixed(2));

                // Initialize itemCounts and totalCount with values from the server
                response.food_quantities.forEach(function (item) {
                    itemCounts[item.food_id] = item.quantity;
                    totalCount += item.quantity;
                    updateQuantityDisplay(item.food_id, item.quantity); // Add this line
                });

                // Update the total count counter button
                $("#total-clicks-counter").text("Total count: " + totalCount);
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


function updateMenuPage() {
    var totalCount = 0;
    var itemCounts = {};
    $(document).ready(function () {
        fetchOrderTotalPrice();

        // Handle clicks on plus sign buttons
        $(".plus-btn").click(function (e) {
            e.preventDefault(); // Prevent the default behavior (navigation)

            // Get the associated item ID
            var itemId = $(this).closest('.category').attr('id');
            console.log("itemId:", itemId)

            // Increment the item count
            if (!itemCounts[itemId]) {
                itemCounts[itemId] = 0;
            }
            itemCounts[itemId]++;

            // Update the total count
            totalCount++;

            // Update the text of the total count counter button
            $("#total-clicks-counter").text("Checkout: " + totalCount);

            // Send an AJAX request to the Django view
            $.ajax({
                url: '/yummy/add_food',
                method: 'POST',
                data: {
                    food_id: itemId,
                    action: 'add',
                    csrfmiddlewaretoken: '{{ csrf_token }}'
                },
                success: function (response) {
                    if (response.success) {
                        console.log("Food added successfully");
                        $("#total-price-counter").text("Total price: $" + response.total_price.toFixed(2));
                        updateQuantityDisplay(itemId, itemCounts[itemId]); // Add this line
                    } else {
                        console.log("An error occurred while adding the food");
                    }
                },
                error: function (response) {
                    console.log("An error occurred while adding the food");
                }
            });
        });

        // Handle clicks on minus sign buttons
        $(".minus-btn").click(function (e) {
            e.preventDefault(); // Prevent the default behavior (navigation)

            // Get the associated item ID
            var itemId = $(this).closest('.category').attr('id');

            // Check if the minus button is associated with an item that has a positive count
            if (itemCounts[itemId] && itemCounts[itemId] > 0) {
                // Decrement the item count
                itemCounts[itemId]--;

                // Update the total count
                totalCount--;

                // Update the text of the total count counter button
                $("#total-clicks-counter").text("Total count: " + totalCount);

                // Send an AJAX request to the Django view
                $.ajax({
                    url: 'yummy/add_food/',
                    method: 'POST',
                    data: {
                        food_id: itemId,
                        action: 'remove',
                        csrfmiddlewaretoken: '{{ csrf_token }}'
                    },
                    success: function (response) {
                        if (response.success) {
                            console.log("Food removed successfully");
                            $("#total-price-counter").text("Total price: $" + response.total_price.toFixed(2));
                            updateQuantityDisplay(itemId, itemCounts[itemId]); // Add this line
                        } else {
                            console.log("An error occurred while removing the food");
                        }
                    },
                    error: function (response) {
                        console.log("An error occurred while removing the food");
                    }
                });
            }
        });
    });


    // In the success callback of the plus-btn AJAX request
    if (response.success) {
        console.log("Food added successfully");
        $("#total-price-counter").text("Total price: $" + response.total_price.toFixed(2));
        updateQuantityDisplay(itemId, itemCounts[itemId]); // Add this line
    } else {
        console.log("An error occurred while adding the food");
    }

    // In the success callback of the minus-btn AJAX request
    if (response.success) {
        console.log("Food removed successfully");
        $("#total-price-counter").text("Total price: $" + response.total_price.toFixed(2));
        updateQuantityDisplay(itemId, itemCounts[itemId]); // Add this line
    } else {
        console.log("An error occurred while removing the food");
    }
}