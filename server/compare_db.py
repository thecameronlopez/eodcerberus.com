import csv
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Ticket, Transaction, LineItem, Location
from app.old_models import EOD as OldEOD

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
# DATE RANGE
# ---------------------------------
start_date = date(2026, 1, 1)
end_date = date(2026, 1, 20)

# ---------------------------------
# FIELDS
# ---------------------------------
sales_fields = [
    "new", "used", "extended_warranty", "diagnostic_fees",
    "in_shop_repairs", "ebay_sales", "labor", "parts", "delivery"
]
return_fields = ["refunds", "ebay_returns"]

# ---------------------------------
# OUTPUT CSV
# ---------------------------------
output_file = "/home/cameron/db_audit.csv"

# ---------------------------------
# MAIN COMPARISON LOGIC
# ---------------------------------
mismatches = []

# Count EODs in old DB
old_eods_count = old_session.query(OldEOD).filter(
    OldEOD.date.between(start_date, end_date)
).count()

# Count Tickets in new DB
new_tickets_count = new_session.query(Ticket).filter(
    Ticket.ticket_date.between(start_date, end_date)
).count()

# Group old EODs by ticket number
eods_by_ticket = {}
for old_eod in old_session.query(OldEOD).filter(
    OldEOD.date.between(start_date, end_date)
).all():
    eods_by_ticket.setdefault(old_eod.ticket_number, []).append(old_eod)

with open(output_file, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    # Write header
    writer.writerow([
        "Ticket Number",
        "Old Total",
        "New Total",
        "Old Sales",
        "New Sales",
        "Old Returns",
        "New Returns",
        "Mismatch?"
    ])

    for ticket_number, eod_rows in eods_by_ticket.items():
        old_sales_total = sum(
            sum(getattr(eod, f) or 0 for f in sales_fields) for eod in eod_rows
        )
        old_returns_total = sum(
            sum(getattr(eod, f) or 0 for f in return_fields) for eod in eod_rows
        )
        old_net_total = sum(eod.sub_total or 0 for eod in eod_rows)

        ticket = new_session.query(Ticket).filter_by(ticket_number=ticket_number).first()
        if not ticket or not ticket.transactions:
            new_sales_total = new_returns_total = new_net_total = None
        else:
            tx = ticket.transactions[0]
            new_sales_total = sum(li.unit_price for li in tx.line_items if not li.is_return)
            new_returns_total = sum(abs(li.unit_price) for li in tx.line_items if li.is_return)
            new_net_total = new_sales_total - new_returns_total

        is_mismatch = (
            old_net_total != (new_net_total if new_net_total is not None else -1)
        )

        if is_mismatch:
            mismatches.append(ticket_number)

        writer.writerow([
            ticket_number,
            old_net_total,
            new_net_total,
            old_sales_total,
            new_sales_total,
            old_returns_total,
            new_returns_total,
            "YES" if is_mismatch else "NO"
        ])

# Summary
print("✅ DB comparison complete")
print(f"Old EODs count: {old_eods_count}")
print(f"New Tickets count: {new_tickets_count}")
print(f"Total mismatched tickets: {len(mismatches)}")
print(f"CSV written to: {output_file}")
