from flask import Flask, jsonify, request
from flask_cors import CORS
from helpers.camera import capture_photo
import subprocess
from helpers.transcription import transcriber
from helpers.verbwire import mintNFT
import asyncio
from helpers.voicing import play_voice
import os
from audio import main_audio
import webbrowser
import json


app = Flask(__name__)

CORS(app, resources={"/": {"origins": "*"}})


@app.route('/', methods=['GET', 'POST'])
def welcome():
    return jsonify({"response": "hi!"})
"""
@app.route('/intent', methods=["GET", 'POST'])
def intent():
"""

@app.route('/record', methods=["GET", 'POST'])
def record():
    filename = main_audio()
    return filename

@app.route('/user_input', methods=["GET", 'POST'])
def user_input():
    file = record()
    x = transcribe(file)
    return x

@app.route('/transcribe', methods=["GET", 'POST'])
def transcribe(filename):
    text = transcriber(filename)
    return jsonify({"response": text})

@app.route('/talk', methods=["GET", 'POST'])
def talk():
    text = play_voice("I like stickers")
    return jsonify({"response": "success"})

@app.route('/capture', methods=["GET", 'POST'])
def capture():
    capture_photo()
    response = asyncio.run(mintNFT("Teddy Bear #1", "Memory of user with Teddy.ai, DeltaHacks 2023", "https://i.ebayimg.com/images/g/vlIAAOSwikBcR0nA/s-l1200.jpg"))
    response = json.loads(response)
    try:
        url = response["transaction_details"]["blockExplorer"]
    except:
        url = "https://goerli.etherscan.io/token/0x791b1e3ba2088ecce017d1c60934804868691f67?a=0x0e5d299236647563649526cfa25c39d6848101f5"

    webbrowser.open_new(url)

    return response.json()

if __name__ == '__main__':
    app.run(debug=True)