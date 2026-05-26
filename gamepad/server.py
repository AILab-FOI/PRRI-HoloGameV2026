#!/usr/bin/env python3

import os
import sys
import json
import time
import threading
import subprocess

import flask
from flask import Flask, render_template, send_from_directory, request, abort
from flask_socketio import SocketIO, emit

from config import GAMES

GAME = GAMES['ProtocolX']  # change this when multiple games are available
ADDR_OUT = '0.0.0.0'
PORT = 5000

app = Flask(__name__)
app.config['SECRET_KEY'] = 'šekret'
socketio = SocketIO(app, cors_allowed_origins='*')

PLAYERS = 0
GAME_STARTED = False
connected_clients = set()


def key_press(key):
    subprocess.call(['xdotool', 'key', '--clearmodifiers', key])

def key_down(key):
    subprocess.call(['xdotool', 'keydown', '--clearmodifiers', key])

def key_up(key):
    subprocess.call(['xdotool', 'keyup', '--clearmodifiers', key])


def popenAndCall(onExit, *popen_args, **popen_kwargs):
    """
    Launch subprocess with given args/kwargs, then call onExit when it finishes.
    """
    def runInThread():
        proc = subprocess.Popen(popen_args, **popen_kwargs)
        proc.wait()
        onExit()

    thread = threading.Thread(target=runInThread)
    thread.daemon = True
    thread.start()
    return thread


@socketio.on('connect')
def connect():
    global PLAYERS
    print('Client connected:', request.sid)
    connected_clients.add(request.sid)
    PLAYERS += 1


@socketio.on('disconnect')
def disconnect():
    global PLAYERS
    print('Client disconnected:', request.sid)
    connected_clients.discard(request.sid)
    PLAYERS -= 1


@socketio.on('ctrl')
def handle_message(message):
    global PLAYERS, GAME_STARTED
    print('ctrl', message)
    if not GAME_STARTED:
        emit('error', {'message': "Game hasn't started or stopped running!"}, broadcast=True)
        return

    try:
        msg = json.loads(message['data'])
    except Exception:
        emit('error', {'message': 'Unparsable message from client.'}, broadcast=True)
        return

    cmd = msg.get('cmd')
    context = msg.get('context')
    game = msg.get('game')

    # Validate game and player count
    if game not in GAMES or PLAYERS > GAMES[game]['players']:
        emit('error', {'message': 'Too many players or unknown game.'}, broadcast=True)
        return

    controls = GAMES[game]['controls'][0]

    if cmd in GAMES[game]['toggles']:
        key = controls[cmd]
        if context == 'start':
            print(f"Key Pressed: {cmd} -> {key}")
            key_down(key)
        else:
            print(f"Key Released: {cmd} -> {key}")
            key_up(key)
    elif cmd in GAMES[game]['taps']:
        key = controls[cmd]
        print(f"Key Tapped: {cmd} -> {key}")
        key_press(key)


@app.route('/')
def ctrl():
    global GAME_STARTED

    def game_exit_callback():
        global GAME_STARTED
        GAME_STARTED = False
        socketio.emit('stop')

    # Resolve TIC-80 binary
    src_dir = "/usr/bin/"
    candidates = ['tic80']

    for name in candidates:
        path = os.path.join(src_dir, name)
        if os.path.isfile(path) and os.access(path, os.X_OK):
            tic80_exe = path
            break
    else:
        abort(500, description=f"TIC-80 binary not found or not executable in {path}")

    print("Launching TIC-80 from:", tic80_exe)

    command = ["tic80", "--fs=/home/barica/Desktop/PRRI-HoloGameV2026", "--cmd=load ProtocolX.py & run"]
    popenAndCall(game_exit_callback, *command, cwd=src_dir)
    GAME_STARTED = True

    return render_template('ctrl.html', game='ProtocolX')


@app.route('/start')
def start():
    return render_template('index.html')


@app.route('/images/<path:path>')
def serve_images(path):
    return send_from_directory('images', path)


@app.route('/js/<path:path>')
def serve_js(path):
    return send_from_directory('js', path)


if __name__ == '__main__':
    print(f"Starting server on {ADDR_OUT}:{PORT} …")
    socketio.run(app, host=ADDR_OUT, port=PORT)