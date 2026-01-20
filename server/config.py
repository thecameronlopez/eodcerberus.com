import os 
from dotenv import load_dotenv
from datetime import datetime, timedelta
import redis

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    DEBUG = FLASK_ENV == "development"
    
    # Sessions
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"))
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_PERMANENT = True
    SESSION_COOKIE_SECURE = FLASK_ENV == "production"   # only secure cookies in prod
    SESSION_COOKIE_HTTPONLY = True
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = "cerberus:"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    
    # CORS
    if FLASK_ENV == "production":
        CORS_ORIGINS = ["https://mattsteamportal.com"]
    else:
        CORS_ORIGINS = ["http://localhost:5173",  "http://192.168.1.205:5173",  "http://192.168.1.248:5173", "http://192.168.1.165:5173", "http://192.168.1.181:5173"]  # 0: local; 1: back shop; 2: main office; 3: home pi; 4: home laptop;
    CORS_SUPPORTS_CREDENTIALS = True