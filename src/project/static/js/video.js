function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}

let getRoomId = () => {
    let currentUrl = window.location.href;
    let parts = currentUrl.split("/");
    return parts[parts.length - 2];
}

let constraints = {
    video: {
        width: {
            min: 640,
            ideal: 1920,
            max: 1920
        },
        height: {
            min: 480,
            ideal: 1080,
            max: 1080
        },
    },
    audio: false
}

let leaveChannel = async () => {
    if (channel) {
    await channel.leave();
    await client.logout();
    }
    window.location.href = '/';
}


// Listen for events on the server
const eventSource = new EventSource("/stream/");
eventSource.onmessage = function(event) {
    // Call the updatePlayersList() function when an event is detected
    updatePlayersList();
}


let toggleCamera = async () => {
    let videoTrack = localStream.getTracks().find(track => track.kind === 'video')

    if (videoTrack.enabled) {
        videoTrack.enabled = false
        document.getElementById('camera-btn').style.backgroundColor = 'rgb(255, 80, 80)'
    } else {
        videoTrack.enabled = true
        document.getElementById('camera-btn').style.backgroundColor = 'rgb(179, 102, 249, .9)'
    }
}

const camera_button = document.getElementById('camera-btn')
camera_button.addEventListener('click', toggleCamera)

window.addEventListener('beforeunload', leaveChannel)
const leave_button = document.getElementById('leave-btn')
leave_button.addEventListener('click', leaveChannel)