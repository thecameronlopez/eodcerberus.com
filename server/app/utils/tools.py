from decimal import Decimal, ROUND_HALF_UP

def to_int(value):
    """Safely convert any incoming value to int. Fallback = 0."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0
    
def to_cents(value):
    """  
    Convert any incoming number to integer cents usinf ROUND_HALF_UP
    Accepts floats (dollars), str("9.99") or int
    Returns 0 on invalid input.
    """
    try:
        val = Decimal(str(value))
        cents = (val * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        #multiply by 100 and round to the nearest cent
        return int(cents)
    except (TypeError, ValueError, ArithmeticError):
        return 0
    
def finalize_ticket(ticket):
    for tx in ticket.transactions:
        for li in tx.line_items:
            li.compute_total()
        tx.compute_total()
    ticket.compute_total()
    

def finalize_transaction(transaction):
    for li in transaction.line_items:
        li.compute_total()
    transaction.compute_total()