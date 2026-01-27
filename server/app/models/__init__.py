from .base import Base
from .enums import DepartmentEnum, LocationEnum, SalesCategoryEnum, PaymentTypeEnum, TaxabilitySourceEnum
from .line_item import LineItem
from .ticket import Ticket
from .users import User
from .deductions import Deduction
from .tax_rate import TaxRate
from .transactions import Transaction
from .location import Location
from .tender import Tender



# custom base requires unique db creation in the flask shell
#from app import create_app
#from app.extensions import db
#from app.models.base import Base
#
#app = create_app()
#with app.app_context():
#   Base.metadata.create_all(bind=db.engine)