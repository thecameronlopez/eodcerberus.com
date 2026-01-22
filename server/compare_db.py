import csv
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal, ROUND_HALF_UP

from app.old_models import EOD as OldEOD, Users as OldUsers
from app.models import Ticket, Transaction, LineItem, User, Location, SalesCategoryEnum, PaymentTypeEnum, TaxabilitySourceEnum
from app.models.services.tax_rules import determine_taxability
from app.utils.tools import to_int

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

start_date = date(2026, 1, 1)
end_date = date(2026, 1, 20)

# -------------------------------
# LOCATION & USER MAPS
# -------------------------------
locations = {loc.code: loc for loc in new_session.query(Location).all()}
users_map = {user.id: user for user in new_session.query(User).all()}

# -------------------------------
# CATEGORY & PAYMENT MAPS
# -------------------------------
category_map = {
    "new": SalesCategoryEnum.NEW_APPLIANCE,
    "used": SalesCategoryEnum.USED_APPLIANCE,
    "extended_warranty": SalesCategoryEnum.EXTENDED_WARRANTY,
    "diagnostic_fees": SalesCategoryEnum.DIAGNOSTIC_FEE,
    "in_shop_repairs": SalesCategoryEnum.IN_SHOP_REPAIR,
    "ebay_sales": SalesCategoryEnum.EBAY_SALE,
    "labor": SalesCategoryEnum.LABOR,
    "parts": SalesCategoryEnum.PARTS,
    "delivery": SalesCategoryEnum.DELIVERY,
}

payment_type_map = {
    "card": PaymentTypeEnum.CARD,
    "cash": PaymentTypeEnum.CASH,
    "checks": PaymentTypeEnum.CHECK,
    "stripe": PaymentTypeEnum.STRIPE_PAYMENT,
    "acima": PaymentTypeEnum.ACIMA,
    "tower_loan": PaymentTypeEnum.TOWER_LOAN,
    "ebay_card": PaymentTypeEnum.EBAY_PAYMENT,
}

sales_fields = [
    "new", "used", "extended_warranty", "diagnostic_fees",
    "in_shop_repairs", "ebay_sales", "labor", "parts", "delivery"
]
return_fields = ["refunds", "ebay_returns"]
payment_fields = ["card", "cash", "checks", "stripe", "acima", "tower_loan", "ebay_card"]

# -------------------------------
# FETCH OLD EODS (exclude eBay)
# -------------------------------
old_eods = [
    e for e in old_session.query(OldEOD)
    .filter(OldEOD.date.between(start_date, end_date))
    if e.ebay_sales == 0
]

# Group by ticket number
eods_by_ticket = {}
for eod in old_eods:
    eods_by_ticket.setdefault(eod.ticket_number, []).append(eod)

# -------------------------------
# AUDIT LOGIC
# -------------------------------
results = []

for ticket_number, eod_rows in eods_by_ticket.items():
    # Determine if there is a hack ticket
    hack_ticket_number = None
    if len(str(ticket_number)) == 5 and str(ticket_number).endswith("0"):
        hack_ticket_number = ticket_number
        original_ticket_number = int(str(ticket_number)[:-1])
    else:
        original_ticket_number = ticket_number

    # Merge normal ticket and hack ticket
    merged_eods = []
    for num in [original_ticket_number, hack_ticket_number]:
        if num is None:
            continue
        merged_eods.extend(eods_by_ticket.get(num, []))

    if not merged_eods:
        continue

    user_id = merged_eods[0].user_id
    user = users_map.get(user_id)
    if not user:
        continue

    loc = locations.get(merged_eods[0].location)
    if not loc:
        continue

    # Create in-memory ticket
    ticket = Ticket(
        ticket_number=original_ticket_number,
        ticket_date=merged_eods[0].date,
        user=user,
        location=loc
    )

    # Build transactions
    for eod in merged_eods:
        tx = Transaction(
            ticket=ticket,
            user=user,
            location=loc,
            posted_date=eod.date
        )

        # --- Sales ---
        for field in sales_fields:
            amt = to_int(getattr(eod, field, 0))
            if amt <= 0:
                continue
            category = category_map[field]
            payment_type = PaymentTypeEnum.CASH  # default for audit
            taxable, tax_source = determine_taxability(
                category=category, 
                payment_type=payment_type, 
                location=loc
                )
            tx.line_items.append(LineItem(
                category=category,
                payment_type=payment_type,
                unit_price=amt,
                taxable=taxable,
                taxability_source=tax_source or TaxabilitySourceEnum.PRODUCT_DEFAULT,
                tax_rate=loc.current_tax_rate or 0,
                is_return=False
            ))

        # --- Returns ---
        for field in return_fields:
            amt = to_int(getattr(eod, field, 0))
            if amt <= 0:
                continue
            category = SalesCategoryEnum.LABOR
            payment_type = PaymentTypeEnum.CASH
            taxable, tax_source = determine_taxability(
                category=category, 
                payment_type=payment_type, 
                location=loc
                )
            tx.line_items.append(LineItem(
                category=category,
                payment_type=payment_type,
                unit_price=-amt,
                taxable=taxable,
                taxability_source=tax_source or TaxabilitySourceEnum.PRODUCT_DEFAULT,
                tax_rate=loc.current_tax_rate or 0,
                is_return=True
            ))
        tx.compute_total()
        ticket.transactions.append(tx)

    # Compute totals
    ticket.compute_total()

    # Aggregate old totals
    old_subtotal = sum(to_int(e.sub_total) for e in merged_eods)
    old_total = old_subtotal  # if tax included in old EOD, adjust here if needed

    mismatch = "YES" if ticket.subtotal != old_subtotal else "NO"

    results.append({
        "Original Ticket": original_ticket_number,
        "Hack Ticket": hack_ticket_number or "N/A",
        "Old Subtotal": old_subtotal,
        "New Subtotal": ticket.subtotal,
        "Old Total": old_total,
        "New Total": ticket.total,
        "Mismatch?": mismatch
    })

# Sort mismatches first
results.sort(key=lambda r: r["Mismatch?"] != "YES")

# -------------------------------
# EXPORT CSV
# -------------------------------
csv_path = "/home/cameron/db_audit.csv"
with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    for row in results:
        writer.writerow(row)

print("✅ Audit complete")
print(f"Tickets processed: {len(results)}")
print(f"Mismatches found: {sum(1 for r in results if r['Mismatch?']=='YES')}")
print(f"CSV saved to {csv_path}")
