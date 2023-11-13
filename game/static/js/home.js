isXturn = true;
gameIsOver = false;

const boxes = document.querySelectorAll('.div');
boxes.forEach(box => {
    box.addEventListener('click', handleClick = () => {
        if (!gameIsOver) {
            const boxId = box.id;
            if (box.innerHTML != '') {
                return;
            }
            if (isXturn) {
                box.innerHTML = 'X';
                isXturn = !isXturn;
            } else {
                box.innerHTML = 'O';
                isXturn = !isXturn;
            }

            const dataToSend = {
                id: boxId,
                isXturn: !isXturn,
            };
            // Make AJAX call to Flask route
            fetch('/pvp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dataToSend)
            })
            .then(response => response.json())
            .then(data => {
                if (data.winner == 'X' || data.winner == 'O') {
                    alert(`${data.winner} wins!`);
                    gameIsOver = true;
                }
            })
            .catch(error => console.error(error));
        }
    });
});

const socket = io({autoConnect: false});

document.getElementById('signup').addEventListener('click', () => {
    document.getElementById('gameBoard').classList.toggle('not_playable');

    document.querySelector('.guest_login').style.display = 'none';
    document.querySelector('.chat').style.display = 'flex';
    socket.connect();
})

