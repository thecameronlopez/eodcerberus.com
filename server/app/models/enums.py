from enum import Enum
from sqlalchemy import Enum as SAEnum


#------------------
# PRODUCT CATEGORY
#------------------
class ProductCategoryEnum(str, Enum):
    APPLIANCE = "appliance"
    PART = "part"
    SERVICE = "service"
    
    def __str__(self):
        return self.value
    
ProductCategoryEnumSA = SAEnum(
    ProductCategoryEnum,
    name="product_category_enum",
    native_enum=False,
    validate_strings=True
)

#------------------
# DEPARTMENTS
#------------------
class DepartmentEnum(str, Enum):
    SALES = "sales"
    SERVICE = "service"
    EBAY = "ebay"
    OFFICE = "office"
    
    def __str__(self):
        return self.value

    
DepartmentEnumSA = SAEnum(
    DepartmentEnum, 
    name="department_enum",
    native_enum=False,
    validate_strings=True
)

#------------------
# LOCATIONS
#------------------
class LocationEnum(str, Enum):
    LAKE_CHARLES = "lake_charles"
    JENNINGS = "jennings"
    LAFAYETTE = "lafayette"
    
    def __str__(self):
        return self.value
    

LocationEnumSA = SAEnum(
    LocationEnum,
    name="location_enum",
    native_enum=False,
    validate_strings=True
)

#------------------
# SALES CATEGORY
#------------------
class SalesCategoryEnum(str, Enum):
    NEW_APPLIANCE = "new_appliance"
    USED_APPLIANCE = "used_appliance"
    EXTENDED_WARRANTY = "extended_warranty"
    DIAGNOSTIC_FEE = "diagnostic_fee"
    IN_SHOP_REPAIR = "in_shop_repair"
    LABOR = "labor"
    PARTS = "parts"
    DELIVERY = "delivery"
    EBAY_SALE = "ebay_sale"
    
    def __str__(self):
        return self.value
    
SalesCategoryEnumSA = SAEnum(
    SalesCategoryEnum,
    name="sales_category_enum",
    native_enum=False,
    validate_strings=True
)


#------------------
# PAYMENT TYPE
#------------------
class PaymentTypeEnum(str, Enum):
    CASH = "cash" #+tax
    CHECK = "check" #+ tax
    CARD = "card" #+tax
    EBAY_PAYMENT = "ebay_payment" #+tax
    STRIPE_PAYMENT = "stripe_payment"
    ACIMA = "acima"
    TOWER_LOAN = "tower_loan" #+tax
    
    def __str__(self):
        return self.value
    
PaymentTypeEnumSA = SAEnum(
    PaymentTypeEnum,
    name="payment_type_enum",
    native_enum=False,
    validate_strings=True
)


#------------------
# TAX REASON
#------------------
class TaxabilitySourceEnum(str, Enum):
    PRODUCT_DEFAULT = "product_default"
    PAYMENT_TYPE = "payment_type"
    LOCATION_OVERRIDE = "location_override"
    MANUAL_OVERRIDE = "manual_override"
    
    def __str__(self):
        return self.value
    
TaxabilitySourceEnumSA = SAEnum(
    TaxabilitySourceEnum,
    name="taxability_source_enum",
    native_enum=False,
    validate_strings=True
)



# Tax needs to get added to the above categories and held in a seperate state for processing with an added 10.75%
# Jennings and lafayette will have different tax amounts.