import csv
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Ticket
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

start_date = date(2026, 1, 1)
end_date = date(2026, 1, 20)

# ---------------------------------
# HELPERS
# ---------------------------------

def normalize_ticket_number(ticket_number: int) -> int:
    s = str(ticket_number)
    if len(s) == 5 and s.endswith("0"):
        return int(s[:-1])
    return ticket_number


def is_pos_trailing_zero(ticket_number: int) -> bool:
    s = str(ticket_number)
    return len(s) == 5 and s.endswith("0")


def is_ebay_ticket(ticket_number: int) -> bool:
    return len(str(ticket_number)) > 5


# ---------------------------------
# LOAD DATA
# ---------------------------------

old_eods = old_session.query(OldEOD).filter(
    OldEOD.date.between(start_date, end_date)
).all()

new_tickets = new_session.query(Ticket).filter(
    Ticket.ticket_date.between(start_date, end_date)
).all()

tickets_map = {t.ticket_number: t for t in new_tickets}

# ---------------------------------
# GROUP OLD EODS BY NORMALIZED TICKET
# ---------------------------------

grouped_eods = {}
for eod in old_eods:
    norm = normalize_ticket_number(eod.ticket_number)
    grouped_eods.setdefault(norm, []).append(eod)

# ---------------------------------
# AUDIT LOGIC
# ---------------------------------

results = []

for ticket_number, eods in grouped_eods.items():

    ticket = tickets_map.get(ticket_number)
    line_items = []

    if ticket:
        for tx in ticket.transactions:
            line_items.extend(tx.line_items)

    # NEW totals
    new_sales = sum(li.unit_price for li in line_items if li.unit_price > 0)
    new_returns = sum(abs(li.unit_price) for li in line_items if li.unit_price < 0)
    new_total = new_sales - new_returns

    # OLD totals
    old_sales = 0
    old_returns = 0
    old_total = 0

    for eod in eods:
        old_sales += sum(to_int(getattr(eod, f, 0)) for f in [
            "new", "used", "extended_warranty", "diagnostic_fees",
            "in_shop_repairs", "ebay_sales", "labor", "parts", "delivery"
        ])
        old_returns += sum(to_int(getattr(eod, f, 0)) for f in [
            "refunds", "ebay_returns"
        ])
        old_total += to_int(eod.sub_total)

    mismatch = old_total != new_total

    reason = "OK"
    if mismatch:
        if not ticket:
            reason = "MISSING_TICKET"
        elif not line_items:
            reason = "NO_LINE_ITEMS"
        elif old_sales != new_sales:
            reason = "SALES_DIFF"
        elif old_returns != new_returns:
            reason = "RETURN_DIFF"
        else:
            reason = "ROUNDING_OR_TAX_DIFF"

    results.append({
        "Ticket Number": ticket_number,
        "Old Total": old_total,
        "New Total": new_total,
        "Old Sales": old_sales,
        "New Sales": new_sales,
        "Old Returns": old_returns,
        "New Returns": new_returns,
        "Line Items": len(line_items),
        "Has Trailing 0 EOD": any(is_pos_trailing_zero(e.ticket_number) for e in eods),
        "eBay Ticket": is_ebay_ticket(ticket_number),
        "Mismatch": "YES" if mismatch else "NO",
        "Reason": reason,
    })

# ---------------------------------
# SORT & CSV OUTPUT
# ---------------------------------

results.sort(key=lambda r: r["Mismatch"] != "YES")

csv_path = "/home/cameron/db_audit.csv"

with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    for row in results:
        writer.writerow(row)

print("✅ DB audit complete")
print(f"Old EOD rows: {len(old_eods)}")
print(f"New tickets: {len(new_tickets)}")
print(f"Mismatches: {sum(1 for r in results if r['Mismatch']=='YES')}")
print(f"CSV written to: {csv_path}")
