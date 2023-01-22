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


let playerScore = 0;
let opponentScore = 0;

function updatePlayerScore() {
    playerScore++;
    document.querySelector('.player-count').textContent = playerScore;
}

function updateOpponentScore() {
    opponentScore++;
    document.querySelector('.opponent-count').textContent = opponentScore;
}


let playGame = async () => {
    let video = document.getElementById('user-1');
    let canvas = document.getElementById('canvas-user-1');
    canvas.style.display = 'block'
    canvas.width = video.clientWidth;
    canvas.height = video.clientHeight;
    canvas.style.position = 'absolute';
    canvas.style.top = video.offsetTop + 'px';
    canvas.style.left = video.offsetLeft + 'px';

    let playerctx = canvas.getContext('2d');
    const videoElement = document.getElementsByClassName('video-player')[0];

    //set text on the playerctx canvas
    playerctx.font = '48px serif';
    playerctx.fillStyle = 'white';
    //delete text from the canvas
    playerctx.clearRect(0, 0, canvas.width, canvas.height);
    let screenshotSent = false;

    function countDown(count) {
        if (count === 0) {
            takeScreenshot();
        } else {
            console.log(count);
            setTimeout(() => {
                countDown(count - 1);
            }, 1000);
        }
    }

    function takeScreenshot() {
        const canvasElement = document.createElement('canvas');
        canvasElement.width = videoElement.videoWidth;
        canvasElement.height = videoElement.videoHeight;
        const canvasCtx = canvasElement.getContext('2d');
        canvasCtx.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
        const imgData = canvasElement.toDataURL('image/jpeg', 0.5);
        if (!screenshotSent) {
            fetch('/play_round/' + game_id + '/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify({
                        screenshot: imgData
                    })
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    let score = data.score;
                    let player1Score = document.getElementsByClassName("Player-count")[0];
                    let roundCount = document.getElementsByClassName("Round-count")[0];
                    let player2Score = document.getElementsByClassName("Computer-count")[0];
                    let roundOrResult = document.getElementById("roundOrResult");
                    if (data.hands_detected) {

                        player1Score.textContent = score.User;
                        player2Score.textContent = score.Computer;
                        roundCount.textContent = data.result;

                        playerctx.fillText(data.player_move, 10, 50)
                        playerctx.fillText(data.confidence_score, 10, 100)
                        playerctx.fillText(data.computer_move, canvas.width - 200, 50)
                    }
                    if (data.game_over) {

                        player1Score.textContent = score.User;
                        player2Score.textContent = score.Computer;
                        roundCount.textContent = data.result;

                        playerctx.fillText(data.player_move, 10, 50)
                        playerctx.fillText(data.confidence_score, 10, 100)
                        playerctx.fillText(data.computer_move, canvas.width - 200, 50)

                        roundOrResult.textContent = "Game Over:";
                        let winner = data.winner;
                        roundCount.textContent = "You " + winner + "!";
                        play_button.style.display = 'none'
                        start_button.style.display = 'block'
                        canvas.style.display = 'none'
                    }
                    if (!data.hands_detected) {
                        alert("No hands detected. Please try again.")
                        screenshotSent = false;
                    } else if (data.message === "Invalid move") {
                        alert("Invalid move. Please try again.")
                        screenshotSent = false;
                    } else {
                        screenshotSent = true;
                    }
                }).catch(error => {
                    console.error(
                        'There has been a problem with your fetch operation:',
                        error
                    );
                });
        }
    }


    countDown(1);

    const camera = new Camera(videoElement, {
        onFrame: async () => {},
        width: 1280,
        height: 720
    });
    camera.start();
}

let leaveChannel = async () => {
    let room_code = getRoomId();
    console.log("Leaving room...");
    await channel.leave();
    await client.logout();
    // Use the fetch API to call the leave_room view
    fetch('/leave_room/' + room_code + '/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
            'Accept': 'application/json'
        }
    }).then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log(data.message);
            window.location.href = '/';
        } else {
            console.error(data.message);
        }
    }).catch(error => {
        console.error('There has been a problem with your fetch operation:',error);
    });
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

window.addEventListener('beforeunload', leaveChannel)

const camera_button = document.getElementById('camera-btn')
camera_button.addEventListener('click', toggleCamera)

const play_button = document.getElementById('play-btn')
play_button.addEventListener('click', playGame)

const leave_button = document.getElementById('leave-btn')
leave_button.addEventListener('click', leaveChannel)