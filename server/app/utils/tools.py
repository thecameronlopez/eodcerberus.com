

def to_int(value):
    """Safely convert any incoming value to int. Fallback = 0."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0
    
    
def finalize_ticket(ticket):
    for tx in ticket.transactions:
        tx.compute_total()
    ticket.compute_total()
    
    
def finalize_transaction(transaction):
    for li in transaction.line_items:
        li.compute_total()
    transaction.compute_total()
    
    
