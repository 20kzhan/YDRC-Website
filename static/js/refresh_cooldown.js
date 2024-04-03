function toggleButton(disabled, cooldownSeconds = 10) {
    const button = document.getElementById("refreshButton");

    button.disabled = disabled;

    if (disabled) {
        // Update the display and start the countdown
        button.style.backgroundColor = "gray"; // Change the button color
        button.value = `Refresh Account Type (${cooldownSeconds})`;

        let secondsRemaining = cooldownSeconds;
        const countdownInterval = setInterval(() => {
            secondsRemaining--;
            button.value = `Refresh Account Type (${secondsRemaining})`;

            if (secondsRemaining <= 0) {
                clearInterval(countdownInterval);
                button.value = "Refresh Account Type"; // Clear the countdown text
                toggleButton(false); // Re-enable the button
            }
        }, 1000); // Update every second

    } else {
        // When re-enabling the button
        button.style.backgroundColor = "white"; // Reset any styles if necessary
        button.value = "Refresh Account Type"; // Clear the countdown
    }
}

document.getElementById("refreshForm").onsubmit = function(event){
    event.preventDefault();

    fetch('/refresh_account_type', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if(data.cooldown_remaining){
            toggleButton(true, data.cooldown_remaining);
        } else {
            console.log("No cooldown given. Defaulting to 60 seconds.")
            toggleButton(true, 60);
        }

        if (data.refresh) {
            window.location.reload();
        }
    });
};

window.onload = function() {
    // Instead of triggering the cooldown, check if a cooldown is needed
    fetch('/check_cooldown', { method: 'GET' }) // Assume this endpoint just checks if a cooldown is necessary
    .then(response => response.json())
    .then(data => {
        if(data.cooldown_remaining && data.cooldown_remaining > 0){
            // If a cooldown is active, disable the button
            toggleButton(true, data.cooldown_remaining);
        }
    })
    .catch(error => console.error('Error:', error));
};
