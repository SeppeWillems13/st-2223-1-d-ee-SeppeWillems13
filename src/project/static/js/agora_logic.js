let APP_ID = "171f25c1a1c644389463a00bbcf1fb8e"
let token = null;
let uid = String(Math.floor(Math.random() * 10000))
let client;
let channel
let remoteStream;
let peerConnection;


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
        playerCount.innerHTML = parseInt(playerCount.innerHTML) - 1;
    }
}


let handleMessageFromPeer = async (message, MemberId) => {

    message = JSON.parse(message.text)

    if (message.type === 'newPlayer') {
        // Extract the new player's information from the message
        let newPlayer = message.player;
        // Update the players list and player count in the HTML template
        updatePlayersList(newPlayer, MemberId);
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

let handleUserJoined = async (MemberId) => {
    createOffer(MemberId);
    // Send the new player's information to the other client
    client.sendMessageToPeer({
        text: JSON.stringify({
            'type': 'newPlayer',
            'player': {
                'name': 'Player ' + MemberId,
                'id': MemberId
            }
        })
    }, MemberId);
    updatePlayersList({
        name: 'Player ' + MemberId
    }, MemberId);
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


function updatePlayersList(newPlayer, MemberId) {
    // Get the players list element from the HTML template
    let playersList = document.getElementById('participants__list');
    console.log(playersList)
    // Create a new player element
    let newPlayerElement = document.createElement('li');
    newPlayerElement.id = `player-${MemberId}`;
    newPlayerElement.innerHTML = newPlayer.name;

    // Add the new player element to the players list
    playersList.appendChild(newPlayerElement);

    // Update the player count displayed in the HTML template
    let playerCount = document.getElementById('player-count');
    if (playerCount) {
        playerCount.innerHTML = parseInt(playerCount.innerHTML) + 1;
    }
}