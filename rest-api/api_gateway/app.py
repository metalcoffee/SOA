from flask import Flask, jsonify, request
import requests

app = Flask(__name__)
USER_SERVICE_URL = "http://user-service:5001"

@app.route('/register', methods=['POST'])
def register():
    response = requests.post(f"{USER_SERVICE_URL}/register", json=request.json)
    return jsonify(response.json()), response.status_code

@app.route('/login', methods=['POST'])
def login():
    response = requests.post(f"{USER_SERVICE_URL}/login", json=request.json)
    return jsonify(response.json()), response.status_code

@app.route('/users/<user_id>', methods=['GET', 'PUT'])
def user_profile(user_id):
    if request.method == 'GET':
        response = requests.get(
            f"{USER_SERVICE_URL}/users/{user_id}",
            headers=request.headers
        )
    elif request.method == 'PUT':
        response = requests.put(
            f"{USER_SERVICE_URL}/users/{user_id}",
            json=request.json,
            headers=request.headers
        )
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
