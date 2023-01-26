let video, canvas, playerctx, screenshotSent, bestOf, localStream, game_id, game, videoElement, canvasElement, canvasCtx, imgData

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
if (!roomId) location.href = '/';

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
    await channel.leave();
    await client.logout();
    window.location.href = '/';
}

leaveChannelOffline = async () => {
window.location.href = '/';
}
//const eventSource = new EventSource("/stream/");
//eventSource.onmessage = function(event) {
//    updatePlayersList();
//}

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

let getBestOf = async () => {
    if (host_id && opponent_id) {
        do {
            bestOf = prompt("Best of how many games? (1, 3, 5, 7, 9, 11, 13)");
        }
        while (bestOf % 2 == 0 || bestOf < 1 || bestOf > 13);
    }
}

let showRoundResults = async (data, offline) => {
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

    if (offline) {
    Swal.fire({
        title: title,
        html: `Player chose: ${data.player_move} <br> Computer chose: ${data.opps_move} <br> Result: ${data.result}`,
        icon: icon,
        confirmButtonText: 'OK'
    });
    } else {
    Swal.fire({
        title: title,
        html: `Player chose: ${data.player_move} <br> Opponent chose: ${data.opps_move} <br> Result: ${data.result}`,
        icon: icon,
        confirmButtonText: 'OK'
    });
    }

};


let showRoundOppResults = async (data) => {
    let icon, title, result;
    if (data.result === "Lose") {
        result = "Win"
        icon = 'success';
        title = 'Round Results';
    } else if (data.result === "Win") {
        result = "Lose"
        icon = 'error';
        title = 'Round Results';
    } else if (data.result === "Tie") {
        result = "Tie"
        icon = 'warning';
        title = 'Round Results';
    }
    console.log("TEST 1")
    Swal.fire({
        title: title,
        html: `Player chose: ${data.player_move} <br> Computer chose: ${data.opps_move} <br> Result: ${result}`,
        icon: icon,
        confirmButtonText: 'OK'
    });
};

function wait(ms) {
    return new Promise(resolve => {
        setTimeout(resolve, ms);
    });
}

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

let showGameResultsOpponent = async (data) => {
    let icon, title, message;
    if (data.winner === "Lose") {
        icon = 'success';
        title = 'Game Over';
        message = 'You Win!';
    } else if (data.winner === "Win") {
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


let updateScoreboardOffline = async (data) => {
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
    computerCount.innerHTML = score.Computer;
}


let resetScoreboard = async (data) => {

    // update the round count on the scoreboard
    let roundCount = document.querySelector('.Round-count');
    roundCount.innerHTML = ``;

    // update the player and computer scores on the scoreboard
    let playerCount = document.querySelector('.Player-count');
    playerCount.innerHTML = 0;

    let computerCount = document.querySelector('.Computer-count');
    computerCount.innerHTML = 0;
}

let updateOppScoreboard = async (data) => {
    console.log(data);
    let playerMove = data.opps_move;
    let oppsMove = data.player_move;
    let result = data.result;

    if (result == "Win") {
        result = "Lose";
    }else if (result == "Lose") {
        result = "Win";
    }
    let score = data.score;
    console.log("CHECK SCORE: ", score)
    // update the round count on the scoreboard
    let roundCount = document.querySelector('.Round-count');
    roundCount.innerHTML = `${oppsMove} vs ${playerMove} - ${result}`;

    // update the player and computer scores on the scoreboard
    let playerCount = document.querySelector('.Player-count');
    playerCount.innerHTML = score.User2;

    let computerCount = document.querySelector('.Computer-count');
    computerCount.innerHTML = score.User;
}

let popUpRoundStarter = async () => {
    Swal.fire({
        title: "Round Started!",
        text: "📷 A picture will be taken and sent to the backend for processing. Please wait...",
        icon: "info",
        showConfirmButton: false,
        allowOutsideClick: false,
        willOpen: () => {
            Swal.showLoading();
        }
    });
}

const camera_button = document.getElementById('camera-btn')
camera_button.addEventListener('click', toggleCamera)