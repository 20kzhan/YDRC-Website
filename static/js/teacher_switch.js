document.addEventListener('DOMContentLoaded', function() {
    // Get the current path
    const currentPath = window.location.pathname;

    // Check if the path is /student_switch
    if (currentPath === '/student_switch') {
        // Find the element with class "teacher-return"
        const teacherReturnElement = document.querySelector('.teacher-return');

        // Set the display style to flex
        if (teacherReturnElement) {
            teacherReturnElement.style.display = 'flex';
        }
    }
});
