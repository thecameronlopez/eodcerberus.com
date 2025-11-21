from flask import Blueprint
from .create import creator
from .auth import authorizer
from .read import reader
from .update import updater
from .delete import deleter
from .analytics import analyzer

api_bp = Blueprint("api", __name__, url_prefix="/api")

api_bp.register_blueprint(creator, url_prefix="/create")
api_bp.register_blueprint(authorizer, url_prefix="/auth")
api_bp.register_blueprint(reader, url_prefix="/read")
api_bp.register_blueprint(updater, url_prefix="/update")
api_bp.register_blueprint(deleter, url_prefix="/delete")
api_bp.register_blueprint(analyzer, url_prefix="/analytics")