let APP_ID = "171f25c1a1c644389463a00bbcf1fb8e"
let token = null;
let uid = String(Math.floor(Math.random() * 10000))
let client, channel, remoteStream, peerConnection, opponentId;
let playersList = document.getElementById('participants__list');

const servers = {
    iceServers: [{
        urls: ['stun:stun1.l.google.com:19302', 'stun:stun2.l.google.com:19302']
    }]
}

let init = async () => {
    try {
        client = AgoraRTM.createInstance(APP_ID, {
            enableLogUpload: false
        });
        await client.login({
            uid,
            token
        });
        channel = client.createChannel(getRoomId());
        await channel.join();

        channel.on('MemberJoined', handleUserJoined);
        channel.on('MemberLeft', handleUserLeft);
        channel.on('startGame', handleGameStarted);
        channel.on('startRound', handleRoundStarted);
        channel.on('playRound', handleRoundPlayed);
        channel.on('error', handleError);
        client.on('MessageFromPeer', handleMessageFromPeer);

        const localStream = await navigator.mediaDevices.getUserMedia(constraints);
        document.getElementById('user-1').srcObject = localStream;

        const host_id = document.getElementById('host_id').value;
        const current_user_id = document.getElementById('current_user_id').value;

        toggleStartButton(host_id === current_user_id);
        togglePlayButton(false);
    } catch (error) {
        console.error(error);
    }
}

let handleUserLeft = (MemberId) => {
    document.getElementById('user-2').style.display = 'none'
    document.getElementById('user-1').classList.remove('smallFrame')

    // Find the player element in the HTML template
    let playerToRemove = document.getElementById(`player-${MemberId}`);

    // Remove the player element from the players list
    if (playerToRemove) {
        playerToRemove.remove();
    }

    // Update the player count displayed in the HTML template
    let playerCount = document.getElementById('player-count');
    if (playerCount) {
        let count = parseInt(playerCount.innerHTML.substring(1, playerCount.innerHTML.indexOf(" ")));
        if (count > 2) {
            count = 2;
        }
        count = Math.max(0, count - 1);
        playerCount.innerHTML = `(${count})`;
    }
}

//THESE MESSAGES ARE FOR THE OPPONENT NOT THE HOST:
//HOST GETS HADLED IN THE GAMESTARTED AND ROUNDSTARTED FUNCTIONS
let handleMessageFromPeer = async (message, MemberId) => {
    opponentId = MemberId
    message = JSON.parse(message.text)
    if (message.type === 'newPlayer') {
        // Extract the new player's information from the message
        var user_id = document.getElementById("current_user_id").value;
        updatePlayersList(user_id);
    }

    if (message.type === 'startGame') {
        best_of = message.bestOf
        document.getElementById('best-of').innerHTML = "Scoreboard: Best of: " + best_of;
        let host_id = document.getElementById('host_id').value
        let current_user_id = document.getElementById('current_user_id').value

        if (host_id == current_user_id) {
            let playButton = document.getElementById('start-btn');
            if (playButton) {
                playButton.style.display = 'block';
            }
            let shuffleButton = document.getElementById('play-btn');
            if (shuffleButton) {
                shuffleButton.style.display = 'none';
            }
        }
        Swal.fire({
            title: 'Game Started!',
            text: "Get ready to play!",
            icon: 'success',
            confirmButtonText: 'OK'
        })

    }

    if (message.type === 'playRound') {
        updateOppScoreboard(message);
        showRoundOppResults(message);
    }

    if(message.type === 'startRound') {
    console.log("startRound")
    popUpRoundStarter()
    }
    if (message.type === 'offer') {
        createAnswer(MemberId, message.offer)
    }

    if (message.type === 'answer') {
        addAnswer(message.answer)
    }

    if (message.type === 'candidate') {
        if (peerConnection) {
            await peerConnection.addIceCandidate(message.candidate)
        }
    }

        if (message.type === 'error') {
        Swal.close();
        Swal.fire({
            title: "Error",
            html: "An error occurred. Please try again.",
            icon: "error",
            confirmButtonText: 'OK'
        });
    }
}

let handleGameStarted = async (MemberId) => {
    let playButton = document.getElementById('start-button');
    if (playButton) {
        playButton.style.display = 'none';
    }
    let shuffleButton = document.getElementById('play-button');
    if (shuffleButton) {
        shuffleButton.style.display = 'block';
    }
    client.sendMessageToPeer({
        text: JSON.stringify({
            'type': 'startGame',
        })
    }, MemberId);
}

let handleRoundPlayed = async (MemberId) => {
    client.sendMessageToPeer({
        text: JSON.stringify({
            'type': 'playRound'
        })
    }, MemberId);
}

let handleError = async (MemberId) => {
    client.sendMessageToPeer({
        text: JSON.stringify({
            'type': 'error'
        })
    }, MemberId);
}

let handleRoundStarted = async (MemberId) => {
    client.sendMessageToPeer({
        text: JSON.stringify({
            'type': 'startRound'
        })
    }, MemberId);
}

let handleUserJoined = async (MemberId) => {
    createOffer(MemberId);
    var user_id = document.getElementById("current_user_id").value;
    let user
    fetch(`/get_user/` + user_id + `/`)
        .then(response => response.json())
        .then(data => {
            user = data;
            return data;
        }).then(data => {
            client.sendMessageToPeer({
                text: JSON.stringify({
                    'type': 'newPlayer',
                    'player': {
                        'name': user.name,
                        'id': user_id
                    }
                })
            }, MemberId);
            updatePlayersList(user_id);
        });
}

let createPeerConnection = async (MemberId) => {
    peerConnection = new RTCPeerConnection(servers)

    remoteStream = new MediaStream()
    document.getElementById('user-2').srcObject = remoteStream
    document.getElementById('user-2').style.display = 'block'

    document.getElementById('user-1').classList.add('smallFrame')


    if (!localStream) {
        localStream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false
        })
        document.getElementById('user-1').srcObject = localStream
    }

    localStream.getTracks().forEach((track) => {
        peerConnection.addTrack(track, localStream)
    })

    peerConnection.ontrack = (event) => {
        event.streams[0].getTracks().forEach((track) => {
            remoteStream.addTrack(track)
        })
    }

    peerConnection.onicecandidate = async (event) => {
        if (event.candidate) {
            client.sendMessageToPeer({
                text: JSON.stringify({
                    'type': 'candidate',
                    'candidate': event.candidate
                })
            }, MemberId)
        }
    }
}

let createOffer = async (MemberId) => {
    await createPeerConnection(MemberId)

    let offer = await peerConnection.createOffer()
    await peerConnection.setLocalDescription(offer)

    client.sendMessageToPeer({
        text: JSON.stringify({
            'type': 'offer',
            'offer': offer
        })
    }, MemberId)
}

let createAnswer = async (MemberId, offer) => {
    await createPeerConnection(MemberId)

    await peerConnection.setRemoteDescription(offer)

    let answer = await peerConnection.createAnswer()
    await peerConnection.setLocalDescription(answer)

    client.sendMessageToPeer({
        text: JSON.stringify({
            'type': 'answer',
            'answer': answer
        })
    }, MemberId)
}

let addAnswer = async (answer) => {
    if (!peerConnection.currentRemoteDescription) {
        peerConnection.setRemoteDescription(answer)
    }
}

function toggleStartButton(show) {
    //id: start-btn
    document.getElementById('start-btn').style.display = show ? 'block' : 'none';
}

function togglePlayButton(show) {
    //id: play-btn
    document.getElementById('play-btn').style.display = show ? 'block' : 'none';
}

let updatePlayersList = (MemberId) => {
    let current_user_id = document.getElementById("current_user_id").value;
    let host_id = document.getElementById("host_id").value;
    let opponent_id = document.getElementById("opponent_id").value;

    if (current_user_id == host_id || current_user_id == opponent_id) {
    fetch(`/get_user/` + current_user_id + `/`)
        .then(response => response.json())
        .then(data => {
            let playersList = document.getElementById('participants__list');
            // Get the players list element from the HTML template
            let newPlayerElement = document.createElement('a');
            newPlayerElement.classList.add('participant');
            newPlayerElement.id = `player-${MemberId}`;
            newPlayerElement.href = `/profile/${MemberId}`;

            let newPlayerAvatar = document.createElement('div');
            newPlayerAvatar.classList.add('avatar');
            newPlayerAvatar.classList.add('avatar--medium');

            let newPlayerAvatarImg = document.createElement('img');
            newPlayerAvatarImg.src = `https://picsum.photos/200/300?random=${MemberId}`;

            newPlayerAvatar.appendChild(newPlayerAvatarImg);

            let newPlayerName = document.createElement('p');
            newPlayerName.innerHTML = data.name;

            let newPlayerUsername = document.createElement('span');
            newPlayerUsername.innerHTML = `@${data.email}`;

            newPlayerName.appendChild(newPlayerUsername);

            newPlayerElement.appendChild(newPlayerAvatar);
            newPlayerElement.appendChild(newPlayerName);

            // Add the new player element to the players list
            playersList.appendChild(newPlayerElement);

            let playerCount = document.getElementById('player-count');
            if (playerCount) {
                let count = parseInt(playerCount.innerHTML.substring(1, playerCount.innerHTML.indexOf(" ")));
                count = count + 1 > 2 ? 2 : count + 1 < 0 ? 0 : count + 1;
                playerCount.innerHTML = "(" + count + " Joined)";
            }
        });
        }
}

let startGame = async (players) => {
    let host_id = document.getElementById('host_id').value
    let opponent_id = document.getElementById('opponent_id').value
    getBestOf();
    document.getElementById('best-of').innerHTML = "Scoreboard: Best of: " + bestOf;
    let response = await fetch('/start_game_online/' + roomId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            bestOf: bestOf,
            host_id: host_id,
            opponent_id: opponent_id
        })
    });
    let data = await response.json();

    if (data.success) {
        client.sendMessageToPeer({
            text: JSON.stringify({
                'type': 'startGame',
                'game_id': data.game_id,
                'bestOf': bestOf
            })
        }, opponentId);

        console.log("Game started successfully");
        play_button.style.display = 'block'
        start_button.style.display = 'none'
        game = data.game;
        game_id = data.game_id;
    } else {
        console.log("Error starting game: " + data.message);
    }
}

let playGame = async () => {
    let video = document.getElementById('user-1');
    let canvas = document.getElementById('canvas-user-1');
    let video_user2 = document.getElementById('user-2');
    let canvas_user2 = document.getElementById('canvas-user-2');
    canvas.style.display = 'block'
    canvas.width = video.clientWidth;
    canvas.height = video.clientHeight;
    canvas.style.position = 'absolute';
    canvas.style.top = video.offsetTop + 'px';
    canvas.style.left = video.offsetLeft + 'px';

    let playerctx = canvas.getContext('2d');
    const videoElement = document.getElementsByClassName('video-player')[0];
    const videoElement_user2 = document.getElementsByClassName('video-player')[1];

    let screenshotSent = false;

    let countDown = async (count) => {
    if (count === 0) {
        takeScreenshot();
    } else {
        console.log(count);
        setTimeout(() => {
            countDown(count - 1);
        }, 3000);
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

        const canvasElement_user2 = document.createElement('canvas');
        canvasElement_user2.width = videoElement_user2.videoWidth;
        canvasElement_user2.height = videoElement_user2.videoHeight;
        const canvasCtx_user2 = canvasElement_user2.getContext('2d');
        canvasCtx_user2.drawImage(videoElement_user2, 0, 0, canvasElement_user2.width, canvasElement_user2.height);
        const imgData_user2 = canvasElement_user2.toDataURL('image/jpeg', 0.5);

        if (!screenshotSent) {
            client.sendMessageToPeer({
                text: JSON.stringify({
                    'type': 'startRound',
                })
            }, opponentId);
            fetch('/get_round_prediction_online/' + game_id + '/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify({
                        screenshot1: imgData,
                        screenshot2: imgData_user2
                    })
                })
                .then(response => response.json())
                .then(data => {
                    Swal.close();
                    if (!data.success) {
                        Swal.fire({
                            title: "Error",
                            html: "An error occurred. Please try again.",
                            icon: "error",
                            confirmButtonText: 'OK'
                        });
                        client.sendMessageToPeer({
                            text: JSON.stringify({
                                'type': 'error',
                                'error': 'An error occurred. Please try again.'
                            })
                        }, opponentId);
                    } else {
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
                        client.sendMessageToPeer({
                            text: JSON.stringify({
                                'type': 'playRound',
                                'player_move': data.opps_move,
                                'opps_move': data.player_move,
                                'score': data.score,
                                'result': data.result,
                                'game_over': data.game_over,
                            })
                        }, opponentId);
                        console.log("YOU PLAYED: " + data.player_move);
                        showRoundResults(data);
                        updateScoreboard(data);
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

    countDown(3);

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

window.addEventListener('beforeunload', leaveChannel)
const leave_button = document.getElementById('leave-btn')
leave_button.addEventListener('click', leaveChannel)

init();