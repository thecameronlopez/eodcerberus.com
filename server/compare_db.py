import csv
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Ticket, Transaction, LineItem
from app.old_models import EOD as OldEOD
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

# -------------------------------
# DATE RANGE
# -------------------------------

start_date = date(2026, 1, 1)
end_date = date(2026, 1, 20)

# -------------------------------
# FETCH DATA
# -------------------------------

old_eods = old_session.query(OldEOD).filter(
    OldEOD.date.between(start_date, end_date)
).all()

# Build a map by ticket number for quick hack ticket lookup
eods_map = {e.ticket_number: e for e in old_eods}

# -------------------------------
# AUDIT LOGIC
# -------------------------------

results = []

for eod in old_eods:
    ticket_number = eod.ticket_number
    # Check for hack ticket: 5 digits ending in 0
    is_hack = len(str(ticket_number)) == 5 and str(ticket_number).endswith("0")
    original_ticket_number = int(str(ticket_number)[:-1]) if is_hack else ticket_number
    hack_ticket_number = ticket_number if is_hack else None

    # Base EOD (original)
    base_eod = eods_map.get(original_ticket_number)

    # Gather transactions (one per EOD)
    transactions = []

    if base_eod:
        tx = Transaction(date=base_eod.date)
        # Add line items based on old EOD fields
        for field, category in [
            ("new", "new"),
            ("used", "used"),
            ("extended_warranty", "extended_warranty"),
            ("diagnostic_fees", "diagnostic_fees"),
            ("in_shop_repairs", "in_shop_repairs"),
            ("ebay_sales", "ebay_sales"),
            ("labor", "labor"),
            ("parts", "parts"),
            ("delivery", "delivery"),
            ("refunds", "refunds"),
            ("ebay_returns", "ebay_returns"),
        ]:
            value = to_int(getattr(base_eod, field, 0))
            if value != 0:
                li = LineItem(unit_price=value)
                tx.line_items.append(li)
        transactions.append(tx)

    # Add hack transaction if exists
    if hack_ticket_number:
        hack_eod = eods_map.get(hack_ticket_number)
        if hack_eod:
            tx = Transaction(date=hack_eod.date)
            for field, category in [
                ("new", "new"),
                ("used", "used"),
                ("extended_warranty", "extended_warranty"),
                ("diagnostic_fees", "diagnostic_fees"),
                ("in_shop_repairs", "in_shop_repairs"),
                ("ebay_sales", "ebay_sales"),
                ("labor", "labor"),
                ("parts", "parts"),
                ("delivery", "delivery"),
                ("refunds", "refunds"),
                ("ebay_returns", "ebay_returns"),
            ]:
                value = to_int(getattr(hack_eod, field, 0))
                if value != 0:
                    li = LineItem(unit_price=value)
                    tx.line_items.append(li)
            transactions.append(tx)

    # Create virtual ticket
    ticket = Ticket(ticket_number=original_ticket_number)
    ticket.transactions = transactions

    # Compute totals
    ticket.compute_total()  # assumes this sets ticket.sub_total and ticket.total
    computed_subtotal = ticket.sub_total
    computed_total = ticket.total

    # Compute old totals
    old_subtotal = sum(to_int(getattr(base_eod, "sub_total", 0)) + 
                       (to_int(getattr(eods_map.get(hack_ticket_number), "sub_total", 0)) if hack_ticket_number else 0))
    old_total = old_subtotal  # can add tax if needed later

    mismatch = "YES" if computed_subtotal != old_subtotal or computed_total != old_total else "NO"

    results.append({
        "Original Ticket": original_ticket_number,
        "Hack Ticket": hack_ticket_number or "",
        "Old Subtotal": old_subtotal,
        "Old Total": old_total,
        "Computed Subtotal": computed_subtotal,
        "Computed Total": computed_total,
        "Mismatch?": mismatch
    })

# Sort mismatches to top
results.sort(key=lambda r: r["Mismatch?"] != "YES")

# -------------------------------
# CSV OUTPUT
# -------------------------------

csv_path = "/home/cameron/db_audit.csv"
with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    for row in results:
        writer.writerow(row)

print("✅ DB comparison complete")
print(f"Old EODs count: {len(old_eods)}")
print(f"Total tickets checked: {len(results)}")
print(f"Total mismatched tickets: {sum(1 for r in results if r['Mismatch?']=='YES')}")
print(f"CSV written to: {csv_path}")
