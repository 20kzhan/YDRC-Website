document.addEventListener('DOMContentLoaded', () => {
    const selectedValueDiv = document.getElementById('selectedValue');
    const customSelectDiv = document.getElementById('customSelect');
    const optionsContainer = document.getElementById('optionsContainer');
    const hiddenInput = document.getElementById('hiddenInput');

    const options = [
        { text: 'Student', value: 'student' },
        { text: 'Teacher', value: 'teacher' },
        { text: 'Admin', value: 'admin' }
        // ... other options
    ];

    // Populate the options dynamically
    options.forEach(option => {
        const div = document.createElement('div');
        div.textContent = option.text;
        div.addEventListener('click', () => {
            // Set the selected value and hide the options
            selectedValueDiv.textContent = option.text;
            hiddenInput.value = option.value;
            optionsContainer.style.display = 'none';
        });
        optionsContainer.appendChild(div);
    });

    // Toggle options display on click
    customSelectDiv.addEventListener('click', () => {
        const isOptionsVisible = optionsContainer.style.display === 'block';
        optionsContainer.style.display = isOptionsVisible ? 'none' : 'block';
    });

    // Hide options if clicked outside of the dropdown
    window.addEventListener('click', (e) => {
        if (!customSelectDiv.contains(e.target)) {
            optionsContainer.style.display = 'none';
        }
    });
});
