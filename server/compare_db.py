import csv
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Ticket, LineItem
from app.old_models import EOD as OldEOD
from app.utils.tools import to_int

# -----------------------------
# DATABASE CONNECTIONS
# -----------------------------
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

# -----------------------------
# COMPARISON
# -----------------------------
mismatches = 0
results = []

# Fetch old EODs grouped by ticket
eods_by_ticket = {}
for old_eod in old_session.query(OldEOD).filter(
    OldEOD.date.between(start_date, end_date)
):
    eods_by_ticket.setdefault(old_eod.ticket_number, []).append(old_eod)

for ticket_number, eod_rows in eods_by_ticket.items():
    ticket = new_session.query(Ticket).filter_by(ticket_number=ticket_number).first()
    new_line_items_count = len(ticket.transactions[0].line_items) if ticket and ticket.transactions else 0

    old_sales_total = sum(
        sum(to_int(getattr(eod, f, 0)) for f in [
            "new", "used", "extended_warranty", "diagnostic_fees",
            "in_shop_repairs", "ebay_sales", "labor", "parts", "delivery"
        ]) for eod in eod_rows
    )
    old_returns_total = sum(
        sum(to_int(getattr(eod, f, 0)) for f in ["refunds", "ebay_returns"])
        for eod in eod_rows
    )
    old_net_total = sum(to_int(eod.sub_total) for eod in eod_rows)

    new_sales_total = sum(
        li.unit_price for li in ticket.transactions[0].line_items
        if not li.is_return
    ) if ticket and ticket.transactions else 0

    new_returns_total = sum(
        abs(li.unit_price) for li in ticket.transactions[0].line_items
        if li.is_return
    ) if ticket and ticket.transactions else 0

    new_net_total = new_sales_total - new_returns_total

    is_mismatch = (old_net_total != new_net_total)
    if is_mismatch:
        mismatches += 1

    results.append({
        "Ticket Number": ticket_number,
        "Old Total": old_net_total,
        "New Total": new_net_total if ticket else "null",
        "Old Sales": old_sales_total,
        "New Sales": new_sales_total if ticket else "null",
        "Old Returns": old_returns_total,
        "New Returns": new_returns_total if ticket else "null",
        "New Line Items": new_line_items_count,
        "Mismatch?": "YES" if is_mismatch else "NO"
    })

# -----------------------------
# WRITE CSV
# -----------------------------
csv_path = "/home/cameron/db_audit.csv"
with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
    writer.writeheader()
    writer.writerows(results)

# -----------------------------
# SUMMARY
# -----------------------------
print("✅ DB comparison complete")
print(f"Old EODs count: {len(eods_by_ticket)}")
print(f"New Tickets count: {new_session.query(Ticket).filter(Ticket.ticket_date.between(start_date, end_date)).count()}")
print(f"Total mismatched tickets: {mismatches}")
print(f"CSV written to: {csv_path}")
