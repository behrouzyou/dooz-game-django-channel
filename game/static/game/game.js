
const cells = document.querySelectorAll(".cell");
const statusElement = document.getElementById("status");

let mySymbol = null;

socket.onopen = function(){statusElement.textContent = "Connected"}

socket.onmessage = function(event){
    const data = JSON.parse(event.data);

    if (data.reason === "game_state"){
        mySymbol = data.your_symbol;
        renderBoard(data.board);
        updateStatus(data);
    }

    if (data.reason === "players"){
        if (data.players < 2){
            statusElement.textContent = `You are ${mySymbol}. Waiting for opponent...`;
            disableBoard();
        }
    }
}

socket.onclose = function(){
    statusElement.textContent = "Connection closed";
    disableBoard();
}

cells.forEach(function(cell){
    cell.addEventListener("click", function(){
        const position = Number(this.dataset.position);
        socket.send(JSON.stringify({type:"move", position: position}));
    });
});

function renderBoard(board){
    cells.forEach(function(cell, index){cell.textContent = board[index];});
}

function updateStatus(data){
    if (data.players < 2){
        statusElement.textContent = `You are ${mySymbol}. Waiting for opponent...`;
        disableBoard();
        return;
    }

    if (data.finished) {
        if (data.winner === "draw"){
            statusElement.textContent = "Draw!";
        } else {
            if (data.winner === mySymbol) {
                statusElement.textContent = "You won!";
            } else {
                statusElement.textContent = "You lost!";
            }
        }
        disableBoard();
        return;
    }

    if (data.turn === mySymbol){
        statusElement.textContent = `Your turn (${mySymbol})`;
        enableAvailableCells(data.board);
    } else {
        statusElement.textContent = `Opponent's turn (${data.turn})`;
        disableBoard();
    }
}

function enableAvailableCells(board){
    cells.forEach(function (cell, index){
        cell.disabled = board[index] !== "";
    });
}

function disableBoard(){
    cells.forEach(function (cell){cell.disabled = true;});
}
