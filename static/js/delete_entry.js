function deleteEntry(id) {
    if (confirm("Are you sure you want to delete this entry?")) {
        console.log("Deleting entry with id: " + id);
        fetch('/delete_teacher', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ teacher_id: id })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                console.error('Error:', data.error);
                alert("Error deleting entry");
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert("Error deleting entry");
        });
    }
}