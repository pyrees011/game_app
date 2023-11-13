from flask_socketio import SocketIO, send, emit

socketio = SocketIO()

@socketio.on('connect')
def handle_connect():
    print('Client connected')