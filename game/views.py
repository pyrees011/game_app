from flask import Blueprint, render_template, request, session, redirect, url_for, current_app, jsonify
from .models import PVPBoard, PVEBoard
from flask_login import login_required, current_user

views = Blueprint('views', __name__)
PVPboard = PVPBoard()
PVEboard = PVEBoard()

@views.route('/')
@login_required
def homepage():
    return render_template("homepage.html", user=current_user)

@views.route('/pvp', methods=['GET', 'POST'])
@login_required
def pvp():
    global PVPboard
    player1 = 0
    player2 = 0
    draw = 0
    if request.method == "POST":
        data = request.get_json()
        if data:
            boxId = int(data["id"])
            isXturn = data["isXturn"]

            PVPboard.makeMove(boxId, isXturn)
            if PVPboard.checkGameOver():
                if PVPboard.checkTie():# check if it is going in the check tie
                    return jsonify({"winner": "Tie"})
                winner, line = PVPboard.checkWinner() #its not even going in for the win even after winning
                current_app.logger.info(winner)
                current_app.logger.info(line)
                return jsonify({"winner": winner, "line": line}) # fix the return in models....  can't get 2 values
            current_app.logger.info(PVPboard.board)
            return jsonify({"winner": None})
    return render_template("PVPboard.html", board=PVPboard, player1 = player1, player2 = player2, draw = draw)

@views.route('/resetpvp', methods=['GET', 'POST'])
@login_required
def resetpvp():
    global PVPboard
    PVPboard = PVPBoard()
    return redirect(url_for('views.pvp'))

@views.route('/pve', methods=['GET', 'POST'])
@login_required
def pve():
    global PVEboard
    player1 = 0
    player2 = 0
    draw = 0
    if request.method == "POST":
        data = request.get_json()
        if data:
            boxId = int(data["id"]) 

            PVEboard.makeMove(boxId)
            if PVEboard.checkGameOver():
                current_app.logger.info("I am in the checkGameOver")
                if PVEboard.checkTie():
                    return jsonify({"winner": "Tie"})
                return jsonify({"winner": PVEboard.checkWinner()})
            current_app.logger.info(PVEboard.board)
            PVEboard.computerGamePlay()
            if PVEboard.checkGameOver():
                if PVEboard.checkTie():
                    return jsonify({
                        "winner": "Tie",
                        "boxId": PVEboard.computerMoves[-1]
                    })
                return jsonify({
                    "winner": PVEboard.checkWinner(),
                    "boxId": PVEboard.computerMoves[-1]
                })
            current_app.logger.info(PVEboard.board)
            return jsonify({"boxId": PVEboard.computerMoves[-1]})
    return render_template("PVEboard.html", board=PVEboard, player1 = player1, player2 = player2, draw = draw)

@views.route('/resetpve', methods=['GET', 'POST'])
@login_required
def resetpve():
    global PVEboard
    PVEboard = PVEBoard()
    return redirect(url_for('views.pve'))