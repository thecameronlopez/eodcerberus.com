import os 
from dotenv import load_dotenv
from datetime import datetime, timedelta
import redis

load_dotenv()

class Config:
    #-------------------------------
    # App Basics
    #-------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret")
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    DEBUG = os.environ.get("DEBUG", "True") == "True"
    APP_NAME = os.environ.get("APP_NAME", "Cerberus")
    
    
    #-------------------------------
    # Database
    #-------------------------------
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get("SQLALCHEMY_ECHO", "False") == "True"
    
    #-------------------------------
    # Session
    #-------------------------------
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"))
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_PERMANENT = True
    SESSION_COOKIE_SECURE = FLASK_ENV == "production"   # only secure cookies in prod
    SESSION_COOKIE_HTTPONLY = True
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = f"{APP_NAME.lower()}:"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    
    #-------------------------------
    # CORS
    #-------------------------------
    if FLASK_ENV == "production":
        CORS_ORIGINS = ["https://eodcerberus.com"]
    else:
        CORS_ORIGINS = [
            "http://127.0.0.1:5173",
            "http://localhost:5173",  
            "http://eodcerberus.dev",
            "http://192.168.1.205:5173",  
            "http://192.168.1.248:5173", 
            "http://192.168.1.165:5173", 
            "http://192.168.1.181:5173"
            ]  
    CORS_SUPPORTS_CREDENTIALS = True
    
    
    #-------------------------------
    # Mail
    #-------------------------------
    MAIL_SUPPRESS_SEND = os.environ.get("MAIL_SUPPRESS_SEND", "False") == "True"
    
    #-------------------------------
    # Feature Flags
    #-------------------------------
    FEATURE_X_ENABLED = os.environ.get("FEATURE_X_ENABLED", "False") == "True"
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    
    
    
    
class TestConfig(Config):
    FLASK_ENV = "testing"
    DEBUG = True
    TESTING = True
    
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URI", "sqlite:///test.db")
    SQLALCHEMY_ECHO = False
    
    
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False
    
    MAIL_SUPPRESS_SEND = True
    
    CORS_ORIGINS = ["*"]
    
    LOG_LEVEL = "WARNING"