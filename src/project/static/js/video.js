let game;
let game_id;
let localStream;
let bestOf;

let getCookie = (name) => {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}

const csrftoken = getCookie('csrftoken');


let getRoomId = () => {
    let currentUrl = window.location.href;
    let parts = currentUrl.split("/");
    return parts[parts.length - 2];
}

let roomId = getRoomId();
if(!roomId) location.href = '/';

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

const eventSource = new EventSource("/stream/");
eventSource.onmessage = function(event) {
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



let showRoundResults = async (data) => {
    let icon, title;
    if (data.result === "Win") {
        icon = 'success';
        title = 'Round Results';
    } else if (data.result === "Lose") {
        icon = 'error';
        title = 'Round Results';
    } else if (data.result === "Tie") {
        icon = 'warning';
        title = 'Round Results';
    }
    console.log(data)
    Swal.fire({
        title: title,
        html: `Player chose: ${data.player_move} <br> Computer chose: ${data.opps_move} <br> Result: ${data.result}`,
        icon: icon,
        confirmButtonText: 'OK'
    });
};

let showGameResults = async (data) => {
    let icon, title, message;
    if (data.winner === "Win") {
        icon = 'success';
        title = 'Game Over';
        message = 'You Win!';
    } else if (data.winner === "Lose") {
        icon = 'error';
        title = 'Game Over';
        message = 'You Lose!';
    }

    Swal.fire({
        title: title,
        html: message,
        icon: icon,
        confirmButtonText: 'OK'
    });
};

let updateScoreboard = async (data) => {
    console.log(data);
    let playerMove = data.player_move;
    let oppsMove = data.opps_move;
    let result = data.result;
    let score = data.score;

    // update the round count on the scoreboard
    let roundCount = document.querySelector('.Round-count');
    roundCount.innerHTML = `${playerMove} vs ${oppsMove} - ${result}`;

    // update the player and computer scores on the scoreboard
    let playerCount = document.querySelector('.Player-count');
    playerCount.innerHTML = score.User;

    let computerCount = document.querySelector('.Computer-count');
    computerCount.innerHTML = score.User2;
}

const camera_button = document.getElementById('camera-btn')
camera_button.addEventListener('click', toggleCamera)

window.addEventListener('beforeunload', leaveChannel)
const leave_button = document.getElementById('leave-btn')
leave_button.addEventListener('click', leaveChannel)