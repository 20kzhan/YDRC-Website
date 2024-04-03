document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector('form[action="/change_account_type"]');
    const statusMessage = document.getElementById("statusMessage");

    form.addEventListener("submit", function(event) {
        event.preventDefault();

        // Add your logic to collect form data
        const formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json()) // assuming your Flask app sends back JSON
        .then(data => {
            // Update the status message
            statusMessage.textContent = data.message;
            statusMessage.style.color = data.success ? 'green' : 'red'; // Optionally, change color based on success
        })
        .catch(error => {
            // Handle errors here
            statusMessage.textContent = 'An error occurred. Please try again.';
            statusMessage.style.color = 'red';
        });
    });
});