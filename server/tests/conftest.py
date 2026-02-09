import pytest 
from app import create_app
from config import TestConfig
from app.extensions import db as _db
from app.models.base import Base

@pytest.fixture(scope="session")
def app():
    """ Create a test Flask app"""
    app = create_app(TestConfig)
    with app.app_context():
        yield app
        
        
@pytest.fixture(scope="session")
def db(app):
    # Ensure all models are imported so SQLAlchemy knows about them
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=_db.engine)
    yield _db
    Base.metadata.drop_all(bind=_db.engine)
    
    
@pytest.fixture
def client(app, db):
    """ Test client for db tests """
    return app.test_client()


@pytest.fixture
def runner(app):
    """ Runner for Click commands """
    return app.test_cli_runner()
