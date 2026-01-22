import csv
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Ticket, Transaction, LineItem, Location
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

start_date = date(2026, 1, 1)
end_date = date(2026, 1, 20)

# -------------------------------
# FETCH DATA
# -------------------------------

old_eods = old_session.query(OldEOD).filter(
    OldEOD.date.between(start_date, end_date)
).all()

new_tickets = new_session.query(Ticket).filter(
    Ticket.ticket_date.between(start_date, end_date)
).all()

# -------------------------------
# COMPARE LOGIC
# -------------------------------

results = []

# Map tickets by ticket_number for quick access
tickets_map = {t.ticket_number: t for t in new_tickets}

for eod in old_eods:
    ticket_number = eod.ticket_number
    trailing_0 = "YES" if len(str(ticket_number)) == 5 else "NO"
    original_ticket_number = int(str(ticket_number)[:-1]) if trailing_0 == "YES" else ticket_number

    new_ticket = tickets_map.get(original_ticket_number)
    line_items = []

    if new_ticket:
        for tx in new_ticket.transactions:
            line_items.extend(tx.line_items)

    # If this is a trailing-0 ticket, also include its line items
    if trailing_0 == "YES":
        trailing_ticket = tickets_map.get(ticket_number)
        if trailing_ticket:
            for tx in trailing_ticket.transactions:
                line_items.extend(tx.line_items)

    new_sales = sum(li.unit_price for li in line_items if li.unit_price > 0)
    new_returns = sum(abs(li.unit_price) for li in line_items if li.unit_price < 0)
    new_total = new_sales - new_returns
    new_line_items_count = len(line_items)

    old_sales_total = sum(to_int(getattr(eod, f, 0)) for f in [
        "new", "used", "extended_warranty", "diagnostic_fees",
        "in_shop_repairs", "ebay_sales", "labor", "parts", "delivery"
    ])
    old_returns_total = sum(to_int(getattr(eod, f, 0)) for f in ["refunds", "ebay_returns"])
    old_total = to_int(eod.sub_total)

    mismatch = "YES" if old_total != new_total else "NO"
    eod_date = eod.date

    results.append({
        "Ticket Number": ticket_number,
        "Date": eod_date,
        "Old Total": old_total,
        "New Total": new_total,
        "Old Sales": old_sales_total,
        "New Sales": new_sales,
        "Old Returns": old_returns_total,
        "New Returns": new_returns,
        "New Line Items": new_line_items_count,
        "Trailing 0": trailing_0,
        "Original Ticket": original_ticket_number,
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
print(f"New Tickets count: {len(new_tickets)}")
print(f"Total mismatched tickets: {sum(1 for r in results if r['Mismatch?']=='YES')}")
print(f"CSV written to: {csv_path}")
