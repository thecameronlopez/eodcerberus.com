import pytest 
from app import create_app
from config import TestConfig
from app.extensions import db as _db

@pytest.fixture(scope="session")
def app():
    """ Create a test Flask app"""
    app = create_app(TestConfig)
    with app.app_context():
        yield app
        
        
@pytest.fixture(scope="session")
def db(app):
    _db.create_all()
    yield _db
    _db.drop_all()
    
    
@pytest.fixture
def client(app, db):
    """ Test client for db tests """
    return app.test_client()


@pytest.fixture
def runner(app):
    """ Runner for Click commands """
    return app.test_cli_runner()