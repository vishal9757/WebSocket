# app.py

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# Keep track of active rooms and invitations
active_rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('create_room')
def create_room(data):
    room_name = data['room_name']
    username = data['username']
    
    if room_name not in active_rooms:
        active_rooms[room_name] = {'users': [username]}
        emit('room_created', {'room_name': room_name, 'users': active_rooms[room_name]['users']}, broadcast=True)
    else:
        emit('room_exists', {'message': 'Room already exists'}, room=request.sid)

@socketio.on('send_invite')
def send_invite(data):
    room_name = data['room_name']
    invitee = data['invitee']
    
    if room_name in active_rooms and invitee not in active_rooms[room_name]['users']:
        emit('invite_received', {'room_name': room_name, 'inviter': data['inviter']}, room=invitee)
    else:
        emit('invalid_invite', {'message': 'Invalid invitation'}, room=request.sid)

@socketio.on('accept_invite')
def accept_invite(data):
    room_name = data['room_name']
    username = data['username']
    
    if room_name in active_rooms:
        active_rooms[room_name]['users'].append(username)
        emit('invite_accepted', {'room_name': room_name, 'users': active_rooms[room_name]['users']}, broadcast=True)

@socketio.on('decline_invite')
def decline_invite(data):
    room_name = data['room_name']
    username = data['username']
    
    if room_name in active_rooms:
        emit('invite_declined', {'room_name': room_name, 'username': username}, room=request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)
