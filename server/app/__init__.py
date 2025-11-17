from flask import Flask
from config import Config
from app.extensions import db, bcrypt, cors, login_manager, mail, migrate
from app.models import Users
from app.logger import setup_logger

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class) 
    
    logger = setup_logger("cerberus")
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
    
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    cors.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    from app.api import api_bp
    app.register_blueprint(api_bp)
    
    
    @login_manager.user_loader
    def load_user(id):
        return Users.query.get(id)
    
    return app