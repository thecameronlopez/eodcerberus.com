from flask import Flask
from config import Config
from app.extensions import db, bcrypt, cors, login_manager, mail, migrate, ma
from app.models import User
from app.logger import setup_logger

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class) 
    
    logger = setup_logger(app.config.get("APP_NAME", "cerberus"))
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
    
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    ma.init_app(app)
    cors.init_app(
        app,
        origins=app.config.get("CORS_ORIGINS"),
        supports_credentials=app.config.get("CORS_SUPPORTS_CREDENTIALS", True),
    )
    login_manager.init_app(app)
    login_manager.login_view = "api.auth.login"
    login_manager.session_protection = "strong"
    mail.init_app(app)
    
    from app.api import api
    app.register_blueprint(api)
    
    
    @login_manager.user_loader
    def load_user(id):
        return db.session.get(User, id)
    
    if app.config.get("FEATURE_X_ENABLED", False):
        app.logger.info("Feature X is ENABLED in dev")
    
    return app