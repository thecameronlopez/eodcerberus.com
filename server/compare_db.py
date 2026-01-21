# compare_totals.py
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Ticket, Transaction, LineItem, Location
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

# -----------------------------
# CONFIG
# -----------------------------
start_date = date(2026, 1, 1)
end_date = date.today()

# Payment type columns in old DB
payment_type_fields = ["card", "cash", "checks", "stripe", "acima", "tower_loan", "ebay_card"]

# -----------------------------
# RUN COMPARISON
# -----------------------------
mismatched_tickets = []

# Fetch tickets from new DB in date range
tickets = new_session.query(Ticket).filter(
    Ticket.ticket_date.between(start_date, end_date)
).all()

for ticket in tickets:
    ticket_number = ticket.ticket_number

    # --- Aggregate old post-tax total from EOD payment columns ---
    old_eods = old_session.query(OldEOD).filter(
        OldEOD.ticket_number == ticket_number,
        OldEOD.date.between(start_date, end_date)
    ).all()

    if not old_eods:
        continue  # nothing to compare

    old_post_tax_total = sum(
        sum(to_int(getattr(eod, pt, 0)) for pt in payment_type_fields)
        for eod in old_eods
    )

    # --- Compute new total from line items ---
    for tx in ticket.transactions:
        for li in tx.line_items:
            li.compute_total()
        tx.compute_total()
    ticket.compute_total()

    new_total = ticket.total

    # --- Compare ---
    if old_post_tax_total != new_total:
        mismatched_tickets.append({
            "ticket_number": ticket_number,
            "old_total": old_post_tax_total,
            "new_total": new_total
        })

# -----------------------------
# REPORT RESULTS
# -----------------------------
if mismatched_tickets:
    print("\n⚠️ Mismatched tickets found:")
    for m in mismatched_tickets:
        print(f"Ticket {m['ticket_number']}: OLD={m['old_total']} NEW={m['new_total']}")
else:
    print("\n✅ All totals match between old and new DBs.")

print(f"\nTotal mismatches: {len(mismatched_tickets)}")
