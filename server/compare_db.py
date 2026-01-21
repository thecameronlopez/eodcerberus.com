import csv
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Ticket, LineItem
from app.old_models import EOD as OldEOD
from app.utils.tools import to_int

# --------------------------
# DATABASE CONNECTIONS
# --------------------------
OLD_DB_URL = "mysql+pymysql://cameron:Claire18!@127.0.0.1:3306/cerberus"
NEW_DB_URL = "mysql+pymysql://cameron:Claire18!@127.0.0.1:3306/cerberus_"

old_engine = create_engine(OLD_DB_URL)
new_engine = create_engine(NEW_DB_URL)

OldSession = sessionmaker(bind=old_engine)
NewSession = sessionmaker(bind=new_engine)

old_session = OldSession()
new_session = NewSession()

# --------------------------
# DATE RANGE
# --------------------------
start_date = date(2026, 1, 1)
end_date = date(2026, 1, 20)

# --------------------------
# FETCH DATA
# --------------------------
old_eods = old_session.query(OldEOD).filter(
    OldEOD.date.between(start_date, end_date)
).all()

# Map old EODs by ticket number
eods_by_ticket = {}
for eod in old_eods:
    eods_by_ticket.setdefault(eod.ticket_number, []).append(eod)

# --------------------------
# COMPARISON LOGIC
# --------------------------
results = []

for ticket_number, eod_rows in eods_by_ticket.items():
    ticket_number_str = str(ticket_number)
    trailing_0 = "NO"
    original_ticket_number = ticket_number

    if len(ticket_number_str) == 5 and ticket_number_str.endswith("0"):
        trailing_0 = "YES"
        original_ticket_number = int(ticket_number_str[:-1])

    # Aggregate old totals
    old_sales_total = sum(
        sum(to_int(getattr(eod, f, 0)) for f in [
            "new", "used", "extended_warranty", "diagnostic_fees",
            "in_shop_repairs", "ebay_sales", "labor", "parts", "delivery"
        ]) for eod in eod_rows
    )
    old_returns_total = sum(
        sum(to_int(getattr(eod, f, 0)) for f in ["refunds", "ebay_returns"]) for eod in eod_rows
    )
    old_total = sum(to_int(eod.sub_total) for eod in eod_rows)

    # Fetch new ticket
    new_ticket = new_session.query(Ticket).filter_by(ticket_number=original_ticket_number).first()

    if trailing_0 == "YES":
        # Sum line items from original ticket plus trailing-0 ticket if exists
        trailing_ticket = new_session.query(Ticket).filter_by(ticket_number=ticket_number).first()
        line_items = []
        if new_ticket:
            line_items.extend(new_ticket.line_items)
        if trailing_ticket:
            line_items.extend(trailing_ticket.line_items)
    else:
        line_items = new_ticket.line_items if new_ticket else []

    new_total = sum(li.unit_price for li in line_items)
    new_sales = sum(li.unit_price for li in line_items if not li.is_return)
    new_returns = sum(abs(li.unit_price) for li in line_items if li.is_return)
    new_line_items = len(line_items)

    mismatch = "YES" if old_total != new_total else "NO"

    results.append([
        ticket_number, old_total, new_total, old_sales_total, new_sales,
        old_returns_total, new_returns, new_line_items, trailing_0,
        original_ticket_number, mismatch
    ])

# --------------------------
# SORT: mismatches first
# --------------------------
results.sort(key=lambda x: x[-1] == "NO")  # YES first

# --------------------------
# WRITE CSV
# --------------------------
csv_file = "/home/cameron/db_audit.csv"
with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Ticket Number", "Old Total", "New Total", "Old Sales", "New Sales",
        "Old Returns", "New Returns", "New Line Items", "Trailing 0",
        "Original Ticket", "Mismatch?"
    ])
    writer.writerows(results)

# --------------------------
# PRINT SUMMARY
# --------------------------
print("✅ DB comparison complete")
print(f"Old EODs count: {len(old_eods)}")
print(f"New Tickets count: {new_session.query(Ticket).filter(Ticket.line_items.any()).count()}")
print(f"Total mismatched tickets: {sum(1 for r in results if r[-1]=='YES')}")
print(f"CSV written to: {csv_file}")
