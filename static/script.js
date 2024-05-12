function hideCreditCardDetails() {
    var creditCardNumber = document.getElementById('cc-number');
    var maskedNumber = creditCardNumber.value.slice(0, -4).replace(/\d/g, '*') + creditCardNumber.value.slice(-4);
    creditCardNumber.value = maskedNumber;
}

// Function to toggle credit card fields based on payment method selection
function toggleCreditCardFields() {
    var cashOnDelivery = document.getElementById("payment_cash_on_delivery");
    var creditCardFields = document.getElementById("credit-card-fields");

    if (cashOnDelivery.checked) {
        creditCardFields.style.display = "none";
    } else {
        creditCardFields.style.display = "block";
    }
}

// Initially hide the credit card fields
document.addEventListener('DOMContentLoaded', function() {
    var creditCardFields = document.getElementById("credit-card-fields");
    creditCardFields.style.display = "none";

    // Event listeners for payment method selection
    document.getElementById("payment_cash_on_delivery").addEventListener("change", toggleCreditCardFields);
    document.getElementById("payment_debit").addEventListener("change", toggleCreditCardFields);
    document.getElementById("payment_paypal").addEventListener("change", toggleCreditCardFields);
    toggleCreditCardFields(); // Initially hide/show based on default selection

    // Prevent default behavior for same-page links
    const links = document.querySelectorAll('a');
    links.forEach(link => {
        link.addEventListener('click', function(event) {
            const currentUrl = window.location.href;
            if (link.href === currentUrl) {
                event.preventDefault(); // Prevent default link behavior
            }
        });
    });
});