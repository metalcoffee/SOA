import pytest
from ..app import app as flask_app
from ..models import db as _db

@pytest.fixture(scope='module')
def app():
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret'
    })
    yield flask_app

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function', autouse=True)
def db(app):
    _db.app = app
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()
