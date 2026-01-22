import csv
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.old_models import EOD as OldEOD, Users as OldUsers
from app.models import Ticket, Transaction, LineItem, Location, User, SalesCategoryEnum, PaymentTypeEnum, TaxabilitySourceEnum

# -------------------------------
# DATABASE CONNECTIONS
# -------------------------------

OLD_DB_URL = "mysql+pymysql://cameron:Claire18!@127.0.0.1:3306/cerberus"
NEW_DB_URL = "mysql+pymysql://cameron:Claire18!@127.0.0.1:3306/cerberus_"

old_engine = create_engine(OLD_DB_URL)
new_engine = create_engine(NEW_DB_URL)

OldSession = sessionmaker(bind=old_engine)
NewSession = sessionmaker(bind=new_engine)

old_session = OldSession()
new_session = NewSession()

# -------------------------------
# CONFIG
# -------------------------------
start_date = date(2026, 1, 1)
end_date = date(2026, 1, 20)

# Map locations
location_map = {loc.code: loc for loc in new_session.query(Location).all()}

# Map users
users_map = {user.id: user for user in new_session.query(User).all()}

# Category & Payment maps
category_map = {
    "new": SalesCategoryEnum.NEW_APPLIANCE,
    "used": SalesCategoryEnum.USED_APPLIANCE,
    "extended_warranty": SalesCategoryEnum.EXTENDED_WARRANTY,
    "diagnostic_fees": SalesCategoryEnum.DIAGNOSTIC_FEE,
    "in_shop_repairs": SalesCategoryEnum.IN_SHOP_REPAIR,
    "labor": SalesCategoryEnum.LABOR,
    "parts": SalesCategoryEnum.PARTS,
    "delivery": SalesCategoryEnum.DELIVERY
}

payment_type_map = {
    "card": PaymentTypeEnum.CARD,
    "cash": PaymentTypeEnum.CASH,
    "checks": PaymentTypeEnum.CHECK,
    "stripe": PaymentTypeEnum.STRIPE_PAYMENT,
    "acima": PaymentTypeEnum.ACIMA,
    "tower_loan": PaymentTypeEnum.TOWER_LOAN,
    "ebay_card": PaymentTypeEnum.EBAY_PAYMENT
}

sales_fields = list(category_map.keys())
return_fields = ["refunds", "ebay_returns"]
payment_fields = list(payment_type_map.keys())

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def to_int(val):
    return int(val or 0)

def compute_line_item(li, location):
    """Compute tax_amount and total for a line item."""
    unit_price = Decimal(li.unit_price or 0)
    tax_rate = Decimal(location.current_tax_rate or 0)
    if li.taxable:
        li.tax_amount = int((unit_price * tax_rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    else:
        li.tax_amount = 0
    li.total = int(unit_price) + li.tax_amount

def compute_transaction(tx):
    for li in tx.line_items:
        if li.tax_amount is None:
            li.tax_amount = 0
        if li.total is None:
            li.total = 0
    tx.units = len(tx.line_items)
    tx.subtotal = sum((-li.unit_price if li.is_return else li.unit_price) for li in tx.line_items)
    tx.tax_total = sum((-li.tax_amount if li.is_return else li.tax_amount) for li in tx.line_items)
    tx.total = sum(li.total if not li.is_return else -li.total for li in tx.line_items)

def compute_ticket(ticket):
    for tx in ticket.transactions:
        compute_transaction(tx)
    ticket.subtotal = sum(tx.subtotal for tx in ticket.transactions)
    ticket.tax_total = sum(tx.tax_total for tx in ticket.transactions)
    ticket.total = sum(tx.total for tx in ticket.transactions)

# -------------------------------
# FETCH OLD EODs
# -------------------------------
old_eods = old_session.query(OldEOD).filter(
    OldEOD.date.between(start_date, end_date)
).order_by(OldEOD.ticket_number, OldEOD.date).all()

# -------------------------------
# GROUP BY ORIGINAL/HACK TICKET
# -------------------------------
tickets_map = {}
for eod in old_eods:
    if eod.ebay_sales > 0 or eod.ebay_returns > 0:
        continue  # Skip ebay tickets
    
    t_number = eod.ticket_number
    # Determine if hack ticket
    is_hack = len(str(t_number)) == 5 and str(t_number).endswith("0")
    original_ticket_number = int(str(t_number)[:-1]) if is_hack else t_number
    hack_ticket_number = t_number if is_hack else None

    tickets_map.setdefault(original_ticket_number, {"eods": [], "hack": None})
    tickets_map[original_ticket_number]["eods"].append(eod)
    if is_hack:
        tickets_map[original_ticket_number]["hack"] = eod

# -------------------------------
# BUILD TICKETS
# -------------------------------
results = []

for original_ticket_number, data in tickets_map.items():
    all_eods = data["eods"]
    hack_eod = data["hack"]

    # Create ticket (do NOT add to session)
    first_eod = all_eods[0]
    user = users_map.get(first_eod.user_id)
    location = location_map.get(first_eod.location)

    ticket = Ticket(
        ticket_number=original_ticket_number,
        ticket_date=first_eod.date,
        user=user,
        location=location
    )

    # --- Add transaction for original ticket ---
    tx = Transaction(
        ticket=ticket,
        user=user,
        location=location,
        posted_date=first_eod.date
    )

    # Add line items from original EOD
    for eod in all_eods:
        for field in sales_fields:
            amt = to_int(getattr(eod, field, 0))
            if amt > 0:
                li = LineItem(
                    transaction=tx,
                    category=category_map[field],
                    payment_type=PaymentTypeEnum.CASH,
                    unit_price=amt,
                    taxable=True,
                    taxability_source=TaxabilitySourceEnum.PRODUCT_DEFAULT,
                    is_return=False
                )
                compute_line_item(li, location)
                tx.line_items.append(li)
        for field in return_fields:
            amt = to_int(getattr(eod, field, 0))
            if amt > 0:
                li = LineItem(
                    transaction=tx,
                    category=SalesCategoryEnum.LABOR,
                    payment_type=PaymentTypeEnum.CASH,
                    unit_price=amt,
                    taxable=True,
                    taxability_source=TaxabilitySourceEnum.PRODUCT_DEFAULT,
                    is_return=True
                )
                compute_line_item(li, location)
                tx.line_items.append(li)

    ticket.transactions.append(tx)

    # --- Add hack ticket transaction if exists ---
    if hack_eod:
        hack_tx = Transaction(
            ticket=ticket,
            user=user,
            location=location,
            posted_date=hack_eod.date
        )
        for field in sales_fields:
            amt = to_int(getattr(hack_eod, field, 0))
            if amt > 0:
                li = LineItem(
                    transaction=hack_tx,
                    category=category_map[field],
                    payment_type=PaymentTypeEnum.CASH,
                    unit_price=amt,
                    taxable=True,
                    taxability_source=TaxabilitySourceEnum.PRODUCT_DEFAULT,
                    is_return=False
                )
                compute_line_item(li, location)
                hack_tx.line_items.append(li)
        for field in return_fields:
            amt = to_int(getattr(hack_eod, field, 0))
            if amt > 0:
                li = LineItem(
                    transaction=hack_tx,
                    category=SalesCategoryEnum.LABOR,
                    payment_type=PaymentTypeEnum.CASH,
                    unit_price=amt,
                    taxable=True,
                    taxability_source=TaxabilitySourceEnum.PRODUCT_DEFAULT,
                    is_return=True
                )
                compute_line_item(li, location)
                hack_tx.line_items.append(li)
        ticket.transactions.append(hack_tx)

    # Compute totals
    compute_ticket(ticket)

    # Aggregate old totals
    old_total = sum(to_int(e.sub_total) for e in all_eods)
    if hack_eod:
        old_total += to_int(hack_eod.sub_total)

    results.append({
        "Original Ticket": original_ticket_number,
        "Hack Ticket": hack_eod.ticket_number if hack_eod else "N/A",
        "Old Total": old_total,
        "New Subtotal": ticket.subtotal,
        "New Tax Total": ticket.tax_total,
        "New Total": ticket.total,
        "Mismatch?": "YES" if ticket.total != old_total else "NO"
    })

# -------------------------------
# OUTPUT CSV
# -------------------------------
csv_path = "/home/cameron/db_audit.csv"
with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    for row in results:
        writer.writerow(row)

print("✅ Audit complete")
print(f"Tickets checked: {len(results)}")
print(f"CSV written to: {csv_path}")
