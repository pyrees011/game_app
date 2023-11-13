from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask import request, jsonify, render_template, Blueprint, redirect, current_app, url_for, flash
from flask_login import current_user, login_required
import random
from datetime import datetime
import os
from werkzeug.utils import secure_filename


mongo = Blueprint('mongo', __name__)


uri = "mongodb+srv://RaunakBhansali:951203@cluster0.reeyyqp.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['acoount']
users = db['users']
leaderboard = db['leaderboard']


@mongo.route('/createUser', methods=['POST', 'GET'])
def createUser():
    if request.method == "POST":
        current_app.logger.info("I am in the post")
        # data = request.get_json()
        username = request.form['username']
        if username:
            current_app.logger.info(username)

            data = {
                'username': current_user.username,
                'email': current_user.email,
                'games': [
                    {
                    'guest_player': username,
                    'player_wins': 0,
                    'guest_player_wins': 0,
                    'draws': 0,
                    'history': [],
                    }
                ]}

            history = {
                    'games': 1,
                }


            if users.find_one({"username": current_user.username, "email": current_user.email}):
                
                # game_history_data = request.get_json()
                # game_history = game_history_data.get('game_history') 
                users.update_one(
                    {'username': current_user.username, "email": current_user.email},
                    {'$push': {'games.$.history': history}}  #this is not working $ is not finding the history
                )
            
            else:
                users.insert_one(data)
                flash("User created successfully", category="success")


# @mongo.route('/createGame', methods=['POST', 'GET'])
# def createGame():
#     if request.method == "POST":
#         current_app.logger.info("I am in the post")
#         data = request.get_json()
#         player1 = data["player1"]
#         player2 = data["player2"]
        
#         if player1 and player2:
#             current_app.logger.info(player1)

#             data = {
#                 'player1': player1,
#                 'player2': player2,
#                 'history': [],
#             }

#             matching = games.find_one({"player1": player1, 'player2': player2})

#             if matching:
#                 games.update_one(
#                     {"player1": player1, 'player2': player2},
#                     {"$push": {"history": data}}
#                 )
#             else:
#                 games.insert_one(data)
#     return jsonify({"error": "Invalid request"})

@mongo.route('leaderboard', methods=['POST', 'GET'])
def leaderboard():
    if request.method == "POST":
        data = request.get_json()

        if data:
            username = data.get("username")

        if leaderboard.find_one({"username": username}):
            leaderboard.update_one(
                {"username": username},
                {"$inc": {"wins": 1}}
            )
        else:
            leaderboard.insert_one({"username": username, "wins": 1})