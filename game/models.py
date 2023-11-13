import random
from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from .sqlite import getUsername
import re
from flask_login import UserMixin

class PVPBoard:
    def __init__(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
    
    def checkWinner(self):
        lines = [
            [0,1,2], 
            [3,4,5], 
            [6,7,8], 
            [0,3,6], 
            [1,4,7], 
            [2,5,8], 
            [0,4,8], 
            [2,4,6]
        ]

        
        for line in lines:
            row1, col1 = divmod(line[0], 3)
            row2, col2 = divmod(line[1], 3)
            row3, col3 = divmod(line[2], 3)
            if self.board[row1][col1] == self.board[row2][col2] == self.board[row3][col3] != " ":
                return self.board[row1][col1]
            
        return None
    
    def checkTie(self):
        for row in self.board:
            for item in row:
                if item == "":
                    return False
        return True
    
    def checkGameOver(self):
        return self.checkWinner() or self.checkTie()
    
    def makeMove(self, id, isXTurn):
        if 0 <= id < 9:
            row, col = divmod(id, 3)  # Divide id by 3 to get row, use remainder for column
            if self.board[row][col] == "":
                if isXTurn:
                    self.board[row][col] = "X"
                else:
                    self.board[row][col] = "O"
            else:
                raise Exception("Invalid move")
        else:
            raise Exception("Id out of range")
    

class PVEBoard:
    def __init__(self):
        self.board = ["" for _ in range(9)]
        self.winningLines = [
                            [0,1,2],
                            [3,4,5],
                            [6,7,8],
                            [0,3,6],
                            [1,4,7],
                            [2,5,8],
                            [0,4,8],
                            [2,4,6]
                        ]
        self.playerMoves = []
        self.computerMoves = []
        self.middleBox = [4]
        self.corners = [0, 2, 6, 8]
        self.sides = [1, 3, 5, 7]
        self.playerTurn = True
        self.remainingBoxes = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        self.difficulty = "expert"

    def getEmptyBoxes(self):
        emptyBoxes = []
        sides = self._sides()
        for i in range(len(sides)):
            if sides[i] == "":
                emptyBoxes.append(i)
        return emptyBoxes
    
    def getEmptyCorners(self):
        emptyCorners = []
        corners = self._corners()
        for i in range(len(corners)):
            if corners[i] == "":
                emptyCorners.append(i)
        return emptyCorners
    
    def checkWinner(self):
        for line in self.winningLines:
            if self.board[line[0]] == self.board[line[1]] == self.board[line[2]] != " ":
                return self.board[line[0]], line
        return None
    
    def checkTie(self):
        for row in self.board:
            if row == "":
                return False
        return True
    
    def checkGameOver(self):
        return self.checkWinner() or self.checkTie()
    
    def makeMove(self, id):
        if self.board[id] == "":
            self.board[id] = "X"
            self.playerMoves.append(id)
            self.remainingBoxes.remove(id)
        else:
            raise Exception("Invalid move")
        
    def makeComputerMove(self, id):
        self.board[id] = "O"
        self.computerMoves.append(id)
        self.remainingBoxes.remove(id)
    
    def checkIfFirstMove(self):
        if len(self.playerMoves) == 1:
            return True
        return False
    
    def checkIfSecondMove(self):
        if len(self.playerMoves) == 2:
            return True
        return False
    
    def checkIfThirdMove(self):
        if len(self.playerMoves) == 3:
            return True
        return False
    
    def makeFirstMove(self):
        if self.playerMoves[0] in self.corners:
            self.makeComputerMove(4)
        else:
            if self.difficulty == "novice":
                self.makeComputerMove(random.choice(self.corners))
            else:
                playermove = self.playerMoves[0]
                if playermove in self.sides:
                    if playermove == 1:
                        self.makeComputerMove(7)
                    elif playermove == 3:
                        self.makeComputerMove(6)
                    else:
                        self.makeComputerMove(8)
                else:
                    self.makeComputerMove(random.choice(self.corners))

    def checkWinningCondition(self):
        for line in self.winningLines:
            if self.board[line[0]] == self.board[line[1]] == "O" and self.board[line[2]] == "":
                return line[2]
            elif self.board[line[1]] == self.board[line[2]] == "O" and self.board[line[0]] == "":
                return line[0]
            elif self.board[line[0]] == self.board[line[2]] == "O" and self.board[line[1]] == "":
                return line[1]
        return None
    
    def checkBlockingCondition(self):
        for line in self.winningLines:
            if self.board[line[0]] == self.board[line[1]] == "X" and self.board[line[2]] == "":
                return line[2]
            elif self.board[line[1]] == self.board[line[2]] == "X" and self.board[line[0]] == "":
                return line[0]
            elif self.board[line[0]] == self.board[line[2]] == "X" and self.board[line[1]] == "":
                return line[1]
        return None
    
    def makeRandomCornerMoves(self):
        while True:
            box = random.choice(self.corners)
            if box != self.playerMoves[0] and box in self.remainingBoxes:
                self.makeComputerMove(box)
                break


    def findDoubleThreat(self, computerMove):
        copyBoard = self.board.copy()
        copyRemainingBoxes = self.remainingBoxes.copy()

        copyBoard[computerMove] = "O"
        copyRemainingBoxes.remove(computerMove)
        for moves in copyRemainingBoxes:
            copyBoard[moves] = "X"
            threats = 0

            for line in self.winningLines:
                if copyBoard[line[0]] == copyBoard[line[1]] == "X" and copyBoard[line[2]] == "":
                    current_app.logger.info("I am the threat")
                    threats += 1
                elif copyBoard[line[1]] == copyBoard[line[2]] == "X" and copyBoard[line[0]] == "":
                    current_app.logger.info("I am the threat")
                    threats += 1
                elif copyBoard[line[0]] == copyBoard[line[2]] == "X" and copyBoard[line[1]] == "":
                    current_app.logger.info("I am the threat")
                    threats += 1
            if threats == 2:
                return True
            else:
                copyBoard[moves] = ""
                threats = 0
        return False


    def makeSecondMove(self):
        blockingBox = self.checkBlockingCondition()
        if blockingBox:
            self.makeComputerMove(blockingBox)
        else:
            current_app.logger.info("I am in the else")
            if self.playerMoves[0] in self.corners:
                if self.playerMoves[-1] in self.sides:
                    if self.difficulty == "novice":
                        self.makeRandomCornerMoves()
                    else:
                        while True:
                            box = random.choice(self.corners)
                            current_app.logger.info(box)
                            if box != self.playerMoves[0]:
                                if not self.findDoubleThreat(box):
                                    self.makeComputerMove(box)
                                    break
                elif self.playerMoves[-1] in self.corners:
                    self.makeComputerMove(random.choice(self.sides))
            elif self.playerMoves[0] in self.sides:
                if self.playerMoves[-1] in self.corners:
                    if self.difficulty == "novice":
                        self.makeComputerMove(4)
                    else:
                        while True:
                            box = random.choice(self.remainingBoxes)
                            current_app.logger.info(box)
                            if box != self.playerMoves[0]:
                                if not self.findDoubleThreat(box):
                                    self.makeComputerMove(box)
                                    break
                elif self.playerMoves[-1] in self.sides:
                    if self.difficulty == "novice":
                        self.makeRandomCornerMoves()
                    else:
                        while True:
                            box = random.choice(self.corners)
                            current_app.logger.info(box)
                            if box != self.playerMoves[0]:
                                if not self.findDoubleThreat(box):
                                    self.makeComputerMove(box)
                                    break
            else:
                self.makeRandomCornerMoves()
                    


    def makeThirdMove(self):
        winningBox = self.checkWinningCondition()
        if winningBox != None:
            self.makeComputerMove(winningBox)
        blockingBox = self.checkBlockingCondition()
        if blockingBox != None:
            self.makeComputerMove(blockingBox)
        else:
            self.makeComputerMove(random.choice(self.remainingBoxes))

    def makeFourthMove(self):
        winningBox = self.checkWinningCondition()
        if winningBox != None:
            self.makeComputerMove(winningBox)
        blockingBox = self.checkBlockingCondition()
        if blockingBox != None:
            self.makeComputerMove(blockingBox)
        else:
            self.makeComputerMove(random.choice(self.remainingBoxes))


    def computerGamePlay(self):
        if self.checkIfFirstMove():
            current_app.logger.info('I am in the first move')
            self.makeFirstMove()
        elif self.checkIfSecondMove():
            current_app.logger.info('I am in the second move')
            self.makeSecondMove()
        elif self.checkIfThirdMove():
            current_app.logger.info('I am in the third move')
            self.makeThirdMove()
        else:
            current_app.logger.info('I am in the fourth move')
            self.makeFourthMove()


class SignupForm(FlaskForm):

    def username_ckeck(form, field):
        usernames = getUsername()
        if field.data in usernames:
            raise ValidationError("Username already taken!")
        
    def has_special(form, field):
        pattern = r'[^a-zA-Z0-9]'

        if not re.search(pattern, field.data):
            raise ValidationError("Password should contain a special character")

    username = StringField('username', validators=[DataRequired(), username_ckeck, Length(max=20)])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired(), has_special, Length(min=6)])
    confirm_password = PasswordField('confirm_password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(max=20)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('LogIn')

class User(UserMixin):
    def __init__(self, id, username, password, email) -> None:
        self.id = id
        self.username = username
        self.password = password
        self.email = email



            

    
    
        


    

    
    