gameIsOver = false;

const boxes = document.querySelectorAll('.div');
boxes.forEach(box => {
    box.addEventListener('click', handleClick = () => {
        if (!gameIsOver) {
            const boxId = box.id;
            if (box.innerHTML != '') {
                return;
            }
            box.innerHTML = 'X';
            console.log(boxId);

            const dataToSend = {
                id: boxId,
            };
            // Make AJAX call to Flask route
            fetch('/pve', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dataToSend)
            })
            .then(response => response.json())
            .then(data => {
                if (!data.winner) {
                    const boxElement = document.getElementById(data.boxId);
                    console.log(boxElement);
                    boxElement.innerHTML = 'O';
                } else if (data.boxId) {
                    const boxElement = document.getElementById(data.boxId);
                    console.log(boxElement);
                    boxElement.innerHTML = 'O';
                    alert(`${data.winner} wins!`);
                    gameIsOver = true;
                } else {
                    if (data.winner == 'X' || data.winner == 'O') {
                        alert(`${data.winner} wins!`);
                        gameIsOver = true;
                    } else {
                        alert('Tie!');
                        gameIsOver = true;
                    }
                }
            })
            .catch(error => console.error(error));
        }
    });
});