import pytest
import requests_mock
from ..app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()

def test_proxy_register(client):
    with requests_mock.Mocker() as m:
        m.post('http://user-service:5001/register', json={'id': 1}, status_code=201)
        
        response = client.post('/register', json={
            "login": "test",
            "password": "pass",
            "email": "test@example.com"
        })
        
        assert response.status_code == 201
        assert response.json['id'] == 1

def test_proxy_login(client):
    with requests_mock.Mocker() as m:
        m.post('http://user-service:5001/login', json={'access_token': 'test'}, status_code=200)
        
        response = client.post('/login', json={
            "login": "test",
            "password": "pass"
        })
        
        assert response.status_code == 200
        assert response.json['access_token'] == 'test'
