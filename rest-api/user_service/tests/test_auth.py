from ..models import User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def test_register_success(client, db):
    data = {
        "login": "testuser",
        "password": "ValidPass123!",
        "email": "test@example.com"
    }
    response = client.post('/register', json=data)
    assert response.status_code == 201
    assert 'id' in response.json
    assert User.query.count() == 1

def test_register_duplicate_login(client, db):
    client.post('/register', json={
        "login": "testuser",
        "password": "ValidPass123!",
        "email": "test1@example.com"
    })

    response = client.post('/register', json={
        "login": "testuser",
        "password": "AnotherPass123!",
        "email": "test2@example.com"
    })
    assert response.status_code == 400
    assert 'already exists' in response.json['message']

def test_login_success(client, db):
    hashed_pwd = bcrypt.generate_password_hash("ValidPass123!").decode('utf-8')
    user = User(login="testuser", password=hashed_pwd, email="test@example.com")
    db.session.add(user)
    db.session.commit()

    response = client.post('/login', json={
        "login": "testuser",
        "password": "ValidPass123!"
    })
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_login_invalid_credentials(client, db):
    response = client.post('/login', json={
        "login": "nonexistent",
        "password": "wrongpass"
    })
    assert response.status_code == 401
    assert 'Invalid credentials' in response.json['message']
