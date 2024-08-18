document.addEventListener("DOMContentLoaded", function() {
    const editableInput = document.getElementById("user_id");
    const hiddenInput = document.getElementById("hidden_user_id");

    editableInput.addEventListener("input", function() {
        // Update hidden input value with the contenteditable text
        hiddenInput.value = editableInput.textContent.trim();
    });

    // Mimic placeholder behavior
    if (!editableInput.textContent.trim()) {
        editableInput.textContent = editableInput.getAttribute("placeholder");
        editableInput.classList.add("placeholder-style");
    }
    editableInput.addEventListener("focus", function() {
        if (editableInput.classList.contains("placeholder-style")) {
            editableInput.textContent = "";
            editableInput.classList.remove("placeholder-style");
        }
    });
    
    editableInput.addEventListener("blur", function() {
        if (!editableInput.textContent.trim()) {
            editableInput.textContent = editableInput.getAttribute("placeholder");
            editableInput.classList.add("placeholder-style");
        }
    });
});