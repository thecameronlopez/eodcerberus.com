import csv
from collections import defaultdict
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Ticket
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
# HELPERS
# -------------------------------

def normalize_ticket(ticket_number: int):
    s = str(ticket_number)
    if len(s) == 5 and s.endswith("0"):
        return int(s[:-1]), ticket_number
    return ticket_number, None

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
# AGGREGATE OLD DB
# -------------------------------

old_totals = defaultdict(int)
hack_map = defaultdict(set)

for eod in old_eods:
    original, hack = normalize_ticket(eod.ticket_number)
    old_totals[original] += to_int(eod.sub_total)

    if hack:
        hack_map[original].add(hack)

# -------------------------------
# AGGREGATE NEW DB
# -------------------------------

new_totals = {}

for ticket in new_tickets:
    subtotal = 0
    for tx in ticket.transactions:
        for li in tx.line_items:
            subtotal += to_int(li.unit_price)

    new_totals[ticket.ticket_number] = subtotal

# -------------------------------
# BUILD AUDIT ROWS
# -------------------------------

all_ticket_numbers = set(old_totals) | set(new_totals)

rows = []

for ticket_number in sorted(all_ticket_numbers):
    old_amount = old_totals.get(ticket_number, 0)
    new_amount = new_totals.get(ticket_number, 0)

    hacks = ", ".join(str(h) for h in sorted(hack_map.get(ticket_number, [])))

    rows.append({
        "Original Ticket Number": ticket_number,
        "Hack Ticket Number": hacks or "",
        "Old Amount": old_amount,
        "New Amount": new_amount,
        "Mismatch?": "YES" if old_amount != new_amount else "NO",
    })

# Put mismatches at top
rows.sort(key=lambda r: r["Mismatch?"] != "YES")

# -------------------------------
# CSV OUTPUT
# -------------------------------

csv_path = "/home/cameron/db_audit.csv"

with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("✅ DB audit complete")
print(f"Tickets audited: {len(rows)}")
print(f"Mismatches: {sum(1 for r in rows if r['Mismatch?'] == 'YES')}")
print(f"CSV written to: {csv_path}")
