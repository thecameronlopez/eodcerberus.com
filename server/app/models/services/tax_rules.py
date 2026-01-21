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
    SalesCategoryEnum.DELIVERY: True,
    SalesCategoryEnum.EXTENDED_WARRANTY: False,
    SalesCategoryEnum.EBAY_SALE: False,
}


def determine_taxability(*, category, payment_type, location):
    """
    Returns:
        (taxable: bool, source: TaxabilitySourceEnum)
    """

    # Category default
    taxable = SALES_CATEGORY_TAXABILITY.get(category, False)
    source = TaxabilitySourceEnum.PRODUCT_DEFAULT
    #IMPORTANT:
    #Payment type must NEVER override an explicitly non-taxable category
    #Payment type override
    payment_taxable = PAYMENT_TYPE_TAXABILITY.get(payment_type)
    if taxable and payment_taxable is not None:
        taxable = payment_taxable
        source = TaxabilitySourceEnum.PAYMENT_TYPE

    #Location overrides (future-proof)
    if location.code == "lafayette" and category == SalesCategoryEnum.LABOR:
        taxable = True
        source = TaxabilitySourceEnum.LOCATION_OVERRIDE

    return taxable, source
