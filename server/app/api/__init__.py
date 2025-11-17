from flask import Blueprint
from .create import creator
from .auth import authorizer
from .read import reader

api_bp = Blueprint("api", __name__, url_prefix="/api")

api_bp.register_blueprint(creator, url_prefix="/create")
api_bp.register_blueprint(authorizer, url_prefix="/auth")
api_bp.register_blueprint(reader, url_prefix="/read")