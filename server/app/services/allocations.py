from decimal import Decimal, ROUND_HALF_UP
from app.models import LineItemTender


def get_allocatable_item(transaction):
    return [
        li for li in transaction.line_items
        if (li.unit_price or 0) > 0
    ]
    
    
def allocate_tender_to_line_items(transaction, tender):
    """
    Generates LineItemTender row allocating this tender
    across the transactions line items
    """
    
    items = get_allocatable_item(transaction)
    
    if not items:
        return []
    
    total_pretax = sum(li.unit_price for li in items)
    
    remaining_amount = tender.amount
    
    allocations = []
    
    for i, li in enumerate(items):
        is_last = i == len(items) - 1
        
        if is_last:
            applied_total = remaining_amount
        else:
            ratio = Decimal(li.unit_price) / Decimal(total_pretax)
            applied_total = int(
                (Decimal(tender.amount) * ratio)
                .quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            )
            
        remaining_amount -= applied_total
        
        if li.taxable and li.tax_rate:
            divisor = Decimal("1") + Decimal(str(li.tax_rate))
            applied_pretax = int(
                (Decimal(applied_total) / divisor)
                .quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            )
            applied_tax = applied_total - applied_pretax
        else:
            applied_pretax = applied_total
            applied_tax = 0
        
        allocations.append(
            LineItemTender(
                line_item=li,
                tender=tender,
                applied_pretax=applied_pretax,
                applied_tax=applied_tax,
                applied_total=applied_total
            )
        )
        
    return allocations