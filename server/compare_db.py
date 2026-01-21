import csv
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Ticket, LineItem
from app.old_models import EOD as OldEOD
from app.utils.tools import to_int

# ---------------------------------
# DATABASE CONNECTIONS
# ---------------------------------
OLD_DB_URL = "mysql+pymysql://cameron:Claire18!@127.0.0.1:3306/cerberus"
NEW_DB_URL = "mysql+pymysql://cameron:Claire18!@127.0.0.1:3306/cerberus_"

old_engine = create_engine(OLD_DB_URL)
new_engine = create_engine(NEW_DB_URL)

OldSession = sessionmaker(bind=old_engine)
NewSession = sessionmaker(bind=new_engine)

old_session = OldSession()
new_session = NewSession()

# ---------------------------------
# CONFIGURATION
# ---------------------------------
start_date = date(2026, 1, 1)
end_date = date(2026, 1, 20)

sales_fields = [
    "new", "used", "extended_warranty", "diagnostic_fees",
    "in_shop_repairs", "ebay_sales", "labor", "parts", "delivery"
]
return_fields = ["refunds", "ebay_returns"]

# ---------------------------------
# COLLECT OLD AND NEW DATA
# ---------------------------------
eods_by_ticket = {}
for old_eod in old_session.query(OldEOD).filter(
    OldEOD.date.between(start_date, end_date)
):
    eods_by_ticket.setdefault(old_eod.ticket_number, []).append(old_eod)

csv_rows = []

for ticket_number, eod_rows in eods_by_ticket.items():
    ticket = new_session.query(Ticket).filter_by(ticket_number=ticket_number).first()

    old_sales_total = sum(
        sum(to_int(getattr(eod, f, 0)) for f in sales_fields) for eod in eod_rows
    )
    old_returns_total = sum(
        sum(to_int(getattr(eod, f, 0)) for f in return_fields) for eod in eod_rows
    )
    old_total = old_sales_total - old_returns_total

    if ticket:
        tx = ticket.transactions[0] if ticket.transactions else None
        new_sales_total = sum(li.unit_price for li in tx.line_items if not li.is_return) if tx else 0
        new_returns_total = sum(abs(li.unit_price) for li in tx.line_items if li.is_return) if tx else 0
        new_total = new_sales_total - new_returns_total
        line_items_count = len(tx.line_items) if tx else 0
    else:
        new_sales_total = new_returns_total = new_total = 0
        line_items_count = 0

    mismatch = "YES" if old_total != new_total else "NO"

    # Trailing 0 detection
    trailing_0 = "YES" if str(ticket_number).endswith("0") else "NO"
    original_ticket = str(ticket_number).rstrip("0") if trailing_0 == "YES" else str(ticket_number)

    csv_rows.append([
        ticket_number,
        old_total,
        new_total,
        old_sales_total,
        new_sales_total,
        old_returns_total,
        new_returns_total,
        line_items_count,
        trailing_0,
        original_ticket,
        mismatch
    ])

# ---------------------------------
# SORT CSV: mismatches first
# ---------------------------------
csv_rows.sort(key=lambda x: 0 if x[-1] == "YES" else 1)

# ---------------------------------
# WRITE CSV
# ---------------------------------
csv_file_path = "/home/cameron/db_audit.csv"
headers = [
    "Ticket Number", "Old Total", "New Total", "Old Sales", "New Sales",
    "Old Returns", "New Returns", "New Line Items",
    "Trailing 0", "Original Ticket", "Mismatch?"
]

with open(csv_file_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(csv_rows)

print("✅ DB comparison complete")
print(f"Old EODs count: {len(eods_by_ticket)}")
print(f"New Tickets count: {new_session.query(Ticket).count()}")
print(f"Total mismatched tickets: {sum(1 for r in csv_rows if r[-1]=='YES')}")
print(f"CSV written to: {csv_file_path}")
