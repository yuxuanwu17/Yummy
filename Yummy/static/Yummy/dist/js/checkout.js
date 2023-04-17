// Example starter JavaScript for disabling form submissions if there are invalid fields
(() => {
    'use strict'

    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    const forms = document.querySelectorAll('.needs-validation')

    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault()
                event.stopPropagation()
            }

            form.classList.add('was-validated')
        }, false)
    })
})()


function luhnCheck(value) {
    /**
     * The Luhn algorithm works because it takes advantage of the mathematical properties of the credit card number structure.
     * By doubling every second digit and adding the individual digits of the products together with the remaining digits,
     * the algorithm creates a weighted sum that is always divisible by 10 when the credit card number is valid.
     * If there is an error in the credit card number, the sum will most likely not be divisible by 10,
     * causing the Luhn check to fail.
     * @type {number}
     */
    let sum = 0;
    let shouldDouble = false;
    for (let i = value.length - 1; i >= 0; i--) {
        if (value.charAt(i) === " ") continue
        let digit = parseInt(value.charAt(i), 10);

        if (shouldDouble) {
            if ((digit *= 2) > 9) {
                digit -= 9;
            }
        }

        sum += digit;
        shouldDouble = !shouldDouble;
    }

    return (sum % 10) === 0;
}

function validateCard(input) {
    console.log("input.val" + input.value)
    if (!luhnCheck(input.value)) {
        input.setCustomValidity("Invalid credit card number.");
    } else {
        input.setCustomValidity("");
    }
}

function isValidExpirationDate(expiration) {
    const currentDate = new Date();
    const currentMonth = currentDate.getMonth() + 1;
    const currentYear = currentDate.getFullYear();

    const [month, year] = expiration.split('/');
    const expMonth = parseInt(month, 10);
    const expYear = parseInt(year, 10);

    if (!month || !year || isNaN(expMonth) || isNaN(expYear)) {
        return false;
    }

    if (expYear < currentYear || (expYear === currentYear && expMonth < currentMonth)) {
        return false;
    }

    return true;
}

function isValidCVV(cvv) {
    const cvvRegex = /^[0-9]{3,4}$/;
    return cvvRegex.test(cvv);
}


function isValidNameOnCard(name) {
    const nameRegex = /^[a-zA-Z\s]+$/;
    return nameRegex.test(name);
}

function validateNameOnCard(input) {
    input.setCustomValidity(isValidNameOnCard(input.value) ? "" : "Invalid name on card.");
}

function validateCardNumber(input) {
    input.setCustomValidity(luhnCheck(input.value) ? "" : "Invalid credit card number.");
}

function validateExpirationDate(input) {
    input.setCustomValidity(isValidExpirationDate(input.value) ? "" : "Invalid expiration date.");
}

function validateCVV(input) {
    input.setCustomValidity(isValidCVV(input.value) ? "" : "Invalid CVV.");
}