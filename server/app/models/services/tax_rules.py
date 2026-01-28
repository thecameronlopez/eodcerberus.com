from app.models.enums import (
    PaymentTypeEnum,
    SalesCategoryEnum,
    TaxabilitySourceEnum,
)

PAYMENT_TYPE_TAXABILITY = {
    PaymentTypeEnum.CASH: True,
    PaymentTypeEnum.CHECK: True,
    PaymentTypeEnum.CARD: True,
    PaymentTypeEnum.EBAY_PAYMENT: False,
    PaymentTypeEnum.STRIPE_PAYMENT: False,
    PaymentTypeEnum.ACIMA: False,
    PaymentTypeEnum.TOWER_LOAN: True,
}

SALES_CATEGORY_TAXABILITY = {
    SalesCategoryEnum.NEW_APPLIANCE: True,
    SalesCategoryEnum.USED_APPLIANCE: True,
    SalesCategoryEnum.PARTS: True,
    SalesCategoryEnum.LABOR: True,
    SalesCategoryEnum.DIAGNOSTIC_FEE: True,
    SalesCategoryEnum.IN_SHOP_REPAIR: True,
    SalesCategoryEnum.DELIVERY: True,
    SalesCategoryEnum.EXTENDED_WARRANTY: False,
    SalesCategoryEnum.EBAY_SALE: False,
}


def determine_taxability(*, category):
    """
    Returns:
        (taxable: bool, source: TaxabilitySourceEnum)
    """
    
    #Override taxable for Acima payments.

    # Category default
    taxable = SALES_CATEGORY_TAXABILITY.get(category, False)
    source = TaxabilitySourceEnum.PRODUCT_DEFAULT

    return taxable, source
