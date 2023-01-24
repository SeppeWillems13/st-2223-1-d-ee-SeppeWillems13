
let init = async () => {
    localStream = await navigator.mediaDevices.getUserMedia(constraints);
    document.getElementById('user-1').srcObject = localStream;
    play_button.style.display = 'none';
};

let startGame = async () => {
    do {
        bestOf = prompt("Best of how many games? (1, 3, 5, 7, 9, 11, 13)");
    }
    while (bestOf % 2 == 0 || bestOf < 1 || bestOf > 13);

    document.getElementById('best-of').innerHTML = "Scoreboard: Best of: " + bestOf;
    let response = await fetch('/start_game_offline/' + roomId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            bestOf: bestOf
        })
    });
    let data = await response.json();
    if (data.success) {
        console.log("Game started successfully");
        play_button.style.display = 'block';
        start_button.style.display = 'none';
        game = data.game;
        game_id = data.game_id;
        console.log(data);
    } else {
        console.log("Error starting game: " + data.message);
    }
};

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
        Swal.fire({
          title: "Round Started!",
          text: "📷 A picture will be taken and sent to the backend for processing. Please wait...",
          icon: "info",
          showConfirmButton: false,
          allowOutsideClick: false,
          onBeforeOpen: () => {
            Swal.showLoading();
          }
        });


        const canvasElement = document.createElement('canvas');
        canvasElement.width = videoElement.videoWidth;
        canvasElement.height = videoElement.videoHeight;
        const canvasCtx = canvasElement.getContext('2d');
        canvasCtx.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
        const imgData = canvasElement.toDataURL('image/jpeg', 0.5);
        if (!screenshotSent) {
            fetch('/get_round_prediction_offline/' + game_id + '/', {
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
                    Swal.close();
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

                        showRoundResults(data);
                    }
                    if (data.game_over) {

                        player1Score.textContent = score.User;
                        player2Score.textContent = score.Computer;
                        roundCount.textContent = data.result;

                        roundOrResult.textContent = "Game Over:";
                        let winner = data.winner;
                        roundCount.textContent = "You " + winner + "!";
                        play_button.style.display = 'none'
                        start_button.style.display = 'block'
                        canvas.style.display = 'none'

                        if (data.winner === "Win" || data.winner === "Lose") {
                            showGameResults(data);
                        }
                    }
                    if (!data.hands_detected) {
                        alert("No hands detected. Please try again. Try in a brighter room.")
                        screenshotSent = false;
                    } else if (data.message === "Invalid move") {
                        alert("Invalid move. Please try again.")
                        screenshotSent = false;
                    } else {
                        screenshotSent = true;
                    }
                }).catch(error => {
                    console.error('There has been a problem with your fetch operation:', error);
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
};

const start_button = document.getElementById('start-btn')
start_button.addEventListener('click', startGame)

const play_button = document.getElementById('play-btn')
play_button.addEventListener('click', playGame)
init();