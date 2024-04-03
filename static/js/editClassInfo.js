// Function to toggle edit/save
function toggleEditSave() {
    var editBtn = document.getElementById('editButton');
    if(editBtn.innerText === 'Edit Class Info') {
        makeEditable();
        editBtn.innerText = 'Save Changes';
        editBtn.onclick = saveChanges; // Assign saveChanges function to onclick
    } else {
        // Optionally, you might want to implement a save confirmation or similar here
        editBtn.innerText = 'Edit Class Info';
        editBtn.onclick = toggleEditSave; // Reassign this function to onclick
    }
}

// Function to make fields editable
function makeEditable() {
    makeTextFieldEditable('class-title', 'Class Name:');
    makeTextFieldEditable('teacher-intro', 'Teacher Intro:');
    makeTextFieldEditable('class-description', 'Class Description:');
    makeTextFieldEditable('class-schedule', 'Schedule:');
    makeTextFieldEditable('class-plan', 'Class Plan:');
    makeTextFieldEditable('class-requirements', 'Requirements:');
    makeTextFieldEditable('other-notes', 'Additional Notes:');
}

function makeTextFieldEditable(fieldClass, label) {
    var element = document.getElementsByClassName(fieldClass)[0];
    if(element) {
        // Extracting text content, assuming label is in <strong> tag
        var value = element.innerText.replace(label, '').trim();
        var labelSpan = label ? '<span class="edit-label">' + label + '</span>' : '';
        element.outerHTML = labelSpan + '<input type="text" class="' + fieldClass + '" value="' + value + '">';
    }
}

// Function to save changes
function saveChanges() {
    // Collect data from input fields
    var data = {
        'classId': globalVars.classId,
        'className': document.getElementsByClassName('class-title')[0].value,
        'teacherIntro': document.getElementsByClassName('teacher-intro')[0].value,
        'classDescription': document.getElementsByClassName('class-description')[0].value,
        'classSchedule': document.getElementsByClassName('class-schedule')[0].value,
        'classPlan': document.getElementsByClassName('class-plan')[0].value,
        'classRequirements': document.getElementsByClassName('class-requirements')[0].value,
        'otherNotes': document.getElementsByClassName('other-notes')[0].value
    };

    // Send data to server
    fetch('/update_class_info', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        // Handle success - maybe show a message and revert fields to static text
        // You might want to refresh the page or re-render the part of the page that contains the class info
    })
    .catch((error) => {
        console.error('Error:', error);
        // Handle errors here, maybe display a message to the user
    });

    window.location.reload();
}

// Initial setup
document.addEventListener('DOMContentLoaded', function() {
    var editBtn = document.getElementById('editButton');
    editBtn.onclick = toggleEditSave; // Assign toggleEditSave function to onclick
});
