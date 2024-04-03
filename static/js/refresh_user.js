<<<<<<< HEAD
const socket = io();  // Connect to the Socket.IO server

socket.on('connect', () => {
    // Join a room specific to this user's 'sub'
    socket.emit('join', {'room': userSub});
});

socket.on('refresh_page', (data) => {
    if (data.sub === userSub) {  // Check if the refresh should apply to this user
        location.reload(true);  // Refresh the page
    }
});
=======
const socket = io();  // Connect to the Socket.IO server

socket.on('connect', () => {
    // Join a room specific to this user's 'sub'
    socket.emit('join', {'room': userSub});
});

socket.on('refresh_page', (data) => {
    if (data.sub === userSub) {  // Check if the refresh should apply to this user
        location.reload(true);  // Refresh the page
    }
});
>>>>>>> f0664b25e0e2c0621c944bed919f34efc1cc8918
