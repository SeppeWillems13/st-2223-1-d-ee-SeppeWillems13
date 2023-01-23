let APP_ID = "171f25c1a1c644389463a00bbcf1fb8e"
let token = null;
let uid = String(Math.floor(Math.random() * 10000))
let client;
let channel
let remoteStream;
let peerConnection;
let opponentId

let playersList = document.getElementById('participants__list');

const servers = {
    iceServers: [{
        urls: ['stun:stun1.l.google.com:19302', 'stun:stun2.l.google.com:19302']
    }]
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



let handleMessageFromPeer = async (message, MemberId) => {
    opponentId = MemberId
    message = JSON.parse(message.text)
    if (message.type === 'newPlayer') {
        // Extract the new player's information from the message
        var user_id = document.getElementById("current_user_id").value;
        updatePlayersList(user_id);
    }

    if (message.type === 'startGame') {
        let host_id = document.getElementById('host_id').value
        let current_user_id = document.getElementById('current_user_id').value

        if(host_id == current_user_id){
            let playButton = document.getElementById('start-btn');
            if (playButton) {
                playButton.style.display = 'none';
                }
            let shuffleButton = document.getElementById('play-btn');
            if (shuffleButton) {
                shuffleButton.style.display = 'block';
                }
        }

    Swal.fire({
      title: 'Game Started!',
      text: "Get ready to play!",
      icon: 'success',
      confirmButtonText: 'OK'
    })

    }

    if (message.type === 'startRound') {
        updateScoreboard(message);
        if (message.result === "Win") {
            Swal.fire({
                title: 'Round Results',
                html: `Player chose: ${message.opps_move} <br> Opponent chose: ${message.your_move} <br> Result: ${message.result}`,
                icon: 'success',
                confirmButtonText: 'OK'
            });
        }
        else if (message.result === "Lose") {
            Swal.fire({
                title: 'Round Results',
                html: `Player chose: ${message.opps_move} <br> Opponent chose: ${message.your_move} <br> Result: ${message.result}`,
                icon: 'error',
                confirmButtonText: 'OK'
            });
        }
        else if (message.result === "Tie") {
            Swal.fire({
                title: 'Round Results',
                html: `Player chose: ${message.opps_move} <br> Opponent chose: ${message.your_move} <br> Result: ${message.result}`,
                icon: 'warning',
                confirmButtonText: 'OK'
            });
        }
    }

    if (message.type === 'offer') {
        createAnswer(MemberId, message.offer)
    }

    if (message.type === 'answer') {
        addAnswer(message.answer)
    }

    if (message.type === 'candidate') {
        if (peerConnection) {
            peerConnection.addIceCandidate(message.candidate)
        }
    }
}

function updateScoreboard(data) {
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
            'type': 'startGame'
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
            console.log("USER SPECIFIC DATA:")
            console.log(data)
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


let updatePlayersList = (MemberId) => {
    fetch(`/get_user/` + MemberId + `/`)
        .then(response => response.json())
        .then(data => {
            console.log("USER SPECIFIC DATA:");
            console.log(data);

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