"use strict"


function loadPosts() {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (this.readyState !== 4) return
        updatePage(xhr)
    }

    xhr.open("GET", "/Yummy/get_order_total_price/", true)
    xhr.send()
}

function updatePage(xhr) {
    if (xhr.status === 200) {
        let response = JSON.parse(xhr.responseText)
        updatePosts(response)
        return
    }

    if (xhr.status === 0) {
        displayError("Cannot connect to server")
        return
    }

    if (xhr.status === 400) {
        displayError("Bad Parameters")
        return
    }

    if (!xhr.getResponseHeader('content-type') === 'application/json') {
        displayError(`Received status = ${xhr.status}`)
        return
    }

    let response = JSON.parse(xhr.responseText)
    if (response.hasOwnProperty('error')) {
        displayError(response.error)
        return
    }
    displayError(response)
}

function displayError(message) {
    let errorElement = document.getElementById("error")
    errorElement.innerHTML = message
    return errorElement
}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
}

function updateSummary(response) {
    // response:{"success": true, 
    //"total_price": 27.0, 
    //"food_quantities": [{"food_id": 2, "quantity": 1}, {"food_id": 8, "quantity": 1}, {"food_id": 6, "quantity": 1}]}

    let summary_div = document.getElementById('id_order_summary')  //get the dishes that is already on the summary page
    // get the dish and quantity and total price from response
    let response_price = response.total_price
    let response_food_quantity = response.food_quantities  

    for (let i = 0; i<response_food_quantity.length; i++) {
        let new_post = response_post[i]
        if (document.getElementById("id_post_div_"+new_post.id) == null) {
            let new_post_element = makePostElement(new_post)
            post_on_stream.prepend(new_post_element)
        }
    }

}

function makeRowElement(food_quantities) {
    let post_content = `<span id="id_post_text_${post.id}">  ${sanitize(post.content)}  </span>`
    let profile_link = makeProfileLinkHTML(post, 'posts')
    let post_time = makeDateTimeHTML(post, 'posts')
    let comment_input = makeNewCommentBoxHTML(post)

    let element = document.createElement("div")
    element.innerHTML = `<tr id="id_summary_row_${food_quantities.food_id}">` + profile_link + post_content + post_time + comment_input
    return element
}

<table  class="table table-striped align-middle text-center">
    <thead>
      <tr>
        <th scope="col">#</th>
        <th scope="col">Image</th>
        <th scope="col">Dish Name</th>
        <!-- <th scope="col">&nbsp;</th> -->
        <th scope="col">Quantity</th>
        <!-- <th scope="col">&nbsp;</th> -->
        <th scope="col">Price</th>
        <th scope="col">&nbsp;</th>
      </tr>
    </thead>
    <tbody class="table-group-divider fs-5">
      <tr id="id_summary_row_${food.id}">
        <th scope="row">1</th>
        <td>
            <img id="id_dish_picture_1" src="{% static 'img/Fried-pork-dumplings.jpg' %}"
            width="50px"
            style="align-content: center">
        </td>
        <td>Fried Pork Dumplings</td>
        <!-- <td><button type="button" class="btn btn-outline-dark"> - </button></td> -->
        <td><input class="quantity_input" type="number" placeholder="1"></td>
        <!-- <td><button type="button" class="btn btn-outline-dark"> + </button></td> -->
        <td>$10</td>
        <td><button type="button" class="btn btn-outline-dark"">Remove</button></td>
      </tr>
    </tbody>
</table>