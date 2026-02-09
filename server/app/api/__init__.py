from flask import Blueprint

from .auth import bp as auth_bp
from .bootstrap import bootstrapper

from .department import bp as dpt_bp
from .sales_category import bp as category_bp
from .payment_type import bp as payments_bp
from .location import bp as location_bp
from .deduction import bp as deduction_bp
from .taxrate import bp as taxrate_bp
from .line_item import bp as line_item_bp
from .tender import bp as tender_bp
from .line_item_tender import bp as lit_bp
from .transaction import bp as transaction_bp
from .ticket import bp as ticket_bp
from .sales_day import bp as sales_day_bp
from .user import bp as user_bp

api = Blueprint("api", __name__, url_prefix="/api")


api.register_blueprint(auth_bp)
api.register_blueprint(bootstrapper, url_prefix="/bootstrap")

api.register_blueprint(dpt_bp)
api.register_blueprint(category_bp)
api.register_blueprint(payments_bp)
api.register_blueprint(location_bp)
api.register_blueprint(deduction_bp)
api.register_blueprint(taxrate_bp)
api.register_blueprint(line_item_bp)
api.register_blueprint(tender_bp)
api.register_blueprint(lit_bp)
api.register_blueprint(transaction_bp)
api.register_blueprint(ticket_bp)
api.register_blueprint(sales_day_bp)
api.register_blueprint(user_bp)
