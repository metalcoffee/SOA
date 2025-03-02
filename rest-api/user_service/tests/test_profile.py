from flask_jwt_extended import create_access_token
from ..models import User


def test_get_profile_success(client, db):
    user = User(
        login="testuser",
        password="hash",
        email="test@example.com",
        first_name="John",
        last_name="Doe"
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))

    response = client.get(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    assert response.json['first_name'] == "John"
    assert 'password' not in response.json

def test_update_profile(client, db):
    user = User(login="testuser", password="hash", email="old@example.com")
    db.session.add(user)
    db.session.commit()
    
    token = create_access_token(identity=str(user.id))
    
    update_data = {
        "first_name": "Alice",
        "email": "new@example.com",
        "phone": "+1234567890"
    }

    response = client.put(
        f'/users/{user.id}',
        json=update_data,
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    assert response.json['email'] == "new@example.com"
    assert response.json['phone'] == "+1234567890"

def test_unauthorized_access(client, db):
    user1 = User(id=1, login="user1", password="pwd", email="user1@test.com")
    user2 = User(id=2, login="user2", password="pwd", email="user2@test.com")
    db.session.add_all([user1, user2])
    db.session.commit()
    
    token = create_access_token(identity=str(user1.id))
    
    response = client.get(
        '/users/2',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 403
