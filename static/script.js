const socket = io({
    query: { player_id: playerId }
});

let playerHand = [];

function drawCard() {
    socket.emit('drawCard', { player_id: playerId });
}

function renderHand() {
    const handDiv = document.getElementById('hand');
    handDiv.innerHTML = playerHand
        .map(card => `${card.value} of ${card.suit}`)
        .join("<br>");
}

function renderRemainingCards(remainingCards) {
    const deckDiv = document.getElementById('deck');
    deckDiv.innerHTML = remainingCards
        .map(card => `${card.value} of ${card.suit}`)
        .join("<br>");
}

function placeBid() {
    const bid = document.getElementById('bid-input').value;
    socket.emit('placeBid', { player_id: playerId, bid: parseInt(bid) });
}

function passBid() {
    socket.emit('passBid', { player_id: playerId });
}

socket.on('deal', (hand) => {
    playerHand = hand;
    renderHand();
    document.querySelector('button').style.display = 'block'; // Show the draw card button
});

socket.on('updateHand', (hand) => {
    playerHand = hand;
    renderHand();
});

socket.on('remainingCards', (remainingCards) => {
    renderRemainingCards(remainingCards);
});

socket.on('startBidding', () => {
    document.getElementById('bidding-area').style.display = 'block';
});

socket.on('bidPlaced', (data) => {
    console.log(`Player ${data.player_id} placed a bid of ${data.bid}`);
});

socket.on('bidRejected', (data) => {
    console.log(`Player ${data.player_id} had a bid of ${data.bid} rejected`);
});

socket.on('bidPassed', (data) => {
    console.log(`Player ${data.player_id} passed`);
});

socket.on('declareWinner', (data) => {
    console.log(`Player ${data.declarer} is the declarer`);
    playerHand = data.hand;
    renderHand();
});

socket.on('widowCards', (widow) => {
    console.log('You received the widow cards:', widow);
});

socket.on('trumpSet', (data) => {
    console.log(`Trump suit is set to ${data.suit}`);
});

socket.on('startTrickPlay', () => {
    console.log('Trick play phase has started');
});
