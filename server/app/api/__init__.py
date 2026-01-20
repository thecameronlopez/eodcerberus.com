from flask import Blueprint
from .auth import authorizer
from .create import creator
from .update import updator
from .read import reader
from .delete import deleter
from .reports import reporter
from .bootstrap import bootstrapper

api = Blueprint("api", __name__, url_prefix="/api")

api.register_blueprint(authorizer, url_prefix="/auth")
api.register_blueprint(creator, url_prefix="/create")
api.register_blueprint(updator, url_prefix="/update")
api.register_blueprint(reader, url_prefix="/read")
api.register_blueprint(deleter, url_prefix="/delete")
api.register_blueprint(reporter, url_prefix="/reports")
api.register_blueprint(bootstrapper, url_prefix="/bootstrap")