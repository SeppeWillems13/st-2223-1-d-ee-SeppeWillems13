let init = async () => {
    localStream = await navigator.mediaDevices.getUserMedia(constraints);
    document.getElementById('user-1').srcObject = localStream;
    play_button.style.display = 'none';
};

let startGame = async () => {
do {bestOf = prompt("Best of how many games? (1, 3, 5, 7, 9, 11, 13)");}
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

    let countDown = async (count) => {
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
        popUpRoundStarter();
        const canvasElement = document.createElement('canvas');
        canvasElement.width = videoElement.videoWidth;
        canvasElement.height = videoElement.videoHeight;
        const canvasCtx = canvasElement.getContext('2d');
        canvasCtx.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
        const imgData = canvasElement.toDataURL('image/jpeg', 0.5);

        function wait(ms) {
            return new Promise(resolve => {
                setTimeout(resolve, ms);
            });
        }

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
                    if (data.success) {
                        showRoundResults(data);
                        updateScoreboardOffline(data);
                    }
                    if (data.game_over) {
                        showRoundResults(data);
                        wait(3000)
                        .then(() => {
                            Swal.close();
                            if (data.winner === "Win" || data.winner === "Lose") {
                                showGameResults(data);
                            }
                        });

                        const playButton = document.getElementById('start-btn');
                        if (playButton) {
                            playButton.style.display = 'block';
                        }
                        const shuffleButton = document.getElementById('play-btn');
                        if (shuffleButton) {
                            shuffleButton.style.display = 'none';
                        }
                    }


                    if (!data.hands_detected) {
                        Swal.fire({
                            title: "No hands",
                            html: "No hands detected in the image. Please try again.",
                            icon: "error",
                            confirmButtonText: 'OK'
                        });
                    }
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

window.addEventListener('beforeunload', leaveChannelOffline)
const leave_button = document.getElementById('leave-btn')
leave_button.addEventListener('click', leaveChannelOffline)
init();