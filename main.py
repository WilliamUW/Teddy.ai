from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={"/": {"origins": "*"}})

@app.route('/', methods=['GET', 'POST'])
def welcome():
    return jsonify({"response": "hi!"})

if __name__ == '__main__':
    app.run(debug=True)