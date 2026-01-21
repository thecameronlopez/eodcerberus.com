import os
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User, Ticket, Transaction, LineItem, Deduction, Location, DepartmentEnum, SalesCategoryEnum, PaymentTypeEnum, Base, TaxRate
from app.old_models import Users as OldUsers, EOD as OldEOD, Deductions as OldDeductions
from app.models.services.tax_rules import determine_taxability
from app.utils.tools import to_int, finalize_ticket, finalize_transaction


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

today = date.today()


# ---------------------------------
# CREATE INITIAL LOCATION
# ---------------------------------
lake_charles = Location(
    name="Lake Charles",
    address="2600 Common St, Lake Charles, LA 70601",
    code="lake_charles",
    current_tax_rate=0.1075
)
jennings = Location(
    name="Jennings",
    address="314 E. Shankland Ave, Jennings, LA, 70546",
    code="jennings",
    current_tax_rate=0.1050
)
new_session.add_all([lake_charles, jennings])
new_session.flush()  # to get IDs

lc_tax = TaxRate(
    location_id=lake_charles.id,
    rate=0.1075,
    effective_from=today,
    effective_to=None
)
jn_tax = TaxRate(
    location_id=jennings.id,
    rate=0.1050,
    effective_from=today,
    effective_to=None
)
new_session.add_all([lc_tax, jn_tax])
new_session.commit()

print("Locations and tax rates set")


# ---------------------------------
# MAPPINGS
# ---------------------------------
location_map = {
    "lake_charles": lake_charles.id,
    "jennings": jennings.id
}

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






# ---------------------------------
# MIGRATION LOGIC
# ---------------------------------
def migrate_users():
    print("Migrating Users...")
    for old_user in old_session.query(OldUsers).all():
        new_user = User(
            first_name=old_user.first_name,
            last_name=old_user.last_name,
            email=old_user.email,
            password_hash=old_user.password_hash,
            department=DepartmentEnum.SALES,
            is_admin=old_user.is_admin,
            terminated=False,
            location_id=lake_charles.id
        )
        new_session.add(new_user)
    new_session.commit()
    print("Users migrated.")
    
def migrate_deductions():
    print("Migrating Deductions...")
    for old_deduction in old_session.query(OldDeductions).all():
        new_deduction = Deduction(
            user_id=old_deduction.user_id,
            amount=old_deduction.amount,
            reason=old_deduction.reason,
            date=old_deduction.date,
        )
        new_session.add(new_deduction)
    new_session.commit()
    print("Deductions migrated.")
    
    

    
def migrate_eods_to_tickets_and_transactions():
    print("Migrating EODs to Tickets, Transactions, LineItems...")
    
    sales_field = [
        "new", "used", "extended_warranty", "diagnostic_fees",
        "in_shop_repairs", "ebay_sales", "labor", "parts", "delivery"
    ]
    
    return_fields = ["refunds", "ebay_returns"]
    
    payment_type_fields = ["card", "cash", "checks", "stripe", "acima", "tower_loan", "ebay_card"]
    
    users_map = {user.id: user for user in new_session.query(User).all()}
    
    
    def get_payment_type(old_eod):
        for pt_field in payment_type_fields:
            amt = to_int(getattr(old_eod, pt_field, 0))
            if amt > 0:
                return payment_type_map[pt_field]
        return PaymentTypeEnum.CASH #fallback
    
    def distribute_returns(old_eod):
        sales = {f: to_int(getattr(old_eod, f, 0)) for f in sales_field if to_int(getattr(old_eod, f, 0)) > 0}
        
        total_sales = sum(sales.values())
        total_returns = sum(to_int(getattr(old_eod, f, 0)) for f in return_fields)
        
        distributed = {}
        running_total = 0
        
        for field, amt in sales.items():
            portion = (amt * total_returns) // total_sales
            distributed[field] = portion
            running_total += portion
            
        remainder = total_returns - running_total
        if remainder > 0:
            largest_field = max(sales, key=sales.get)
            distributed[largest_field] += remainder
        return list(distributed.items())
        
    
    
    
    for old_eod in old_session.query(OldEOD).all():
        #fetch user
        user = users_map.get(old_eod.user_id)
        if not user:
            print(f"Skipping EOD {old_eod.id} - User {old_eod.user_id} not found.")
            continue
        
        #determin location from user
        loc_id = location_map.get(old_eod.location)
        location = new_session.get(Location, loc_id)
        
        #create ticket
        ticket = Ticket(
            ticket_number=old_eod.ticket_number,
            ticket_date=old_eod.date,
            user_id=user.id,
            location_id=loc_id
        )
        new_session.add(ticket)
        new_session.flush() # generate ticket.id
        
        #create transaction
        transaction = Transaction(
            ticket=ticket,
            user=user,
            location=location,
            posted_date=ticket.ticket_date
        )
        new_session.add(transaction)
        new_session.flush() # generate transaction.id
        
        payment_type = get_payment_type(old_eod)
        
        #procees revenue items
        for field in sales_field:
            amount = to_int(getattr(old_eod, field, 0))
            if amount > 0:
                category = category_map[field]
                
                #determine taxability                    
                taxable, tax_source = determine_taxability(
                    category=category,
                    payment_type=payment_type,
                    location=location
                )
                
                transaction.line_items.append(LineItem(
                    category=category,
                    payment_type=payment_type,
                    unit_price=amount,
                    taxable=taxable,
                    taxability_source=tax_source,
                    tax_rate=location.current_tax_rate or 0,
                    is_return=False
                ))

                
        #process return items
        for field, amount in distribute_returns(old_eod):
            if amount > 0:
                category = category_map[field]
                
                taxable, tax_source = determine_taxability(
                    category=category,
                    payment_type=payment_type,
                    location=location
                )
                
                transaction.line_items.append(
                    LineItem(
                        category=category,
                        payment_type=payment_type,
                        unit_price=-amount,
                        taxable=taxable,
                        taxability_source=tax_source,
                        tax_rate=location.current_tax_rate or 0,
                        is_return=True
                    )
                )
                
        # Compute totals
        finalize_transaction(transaction)
        finalize_ticket(ticket)
        
    new_session.commit()
    print("Migration finished successfully.")
    

# ---------------------------------
# VALIDATE TOTALS
# ---------------------------------
def validate_migration():
    print("\nValidating migration integrity...\n")

    mismatches = 0

    sales_fields = [
        "new", "used", "extended_warranty", "diagnostic_fees",
        "in_shop_repairs", "ebay_sales", "labor", "parts", "delivery"
    ]

    for old_eod in old_session.query(OldEOD).all():

        ticket = new_session.query(Ticket).filter_by(ticket_number=old_eod.ticket_number).first()

        if not ticket:
            print(f"Missing Ticket for EOD {old_eod.ticket_number}")
            mismatches += 1
            continue

        tx = ticket.transactions[0] if ticket.transactions else None
        if not tx:
            print(f"Missing Transaction for Ticket {ticket.ticket_number}")
            mismatches += 1
            continue

        # OLD totals
        old_sales_total = sum(to_int(getattr(old_eod, f, 0)) for f in sales_fields)
        old_returns_total = to_int(old_eod.refunds) + to_int(old_eod.ebay_returns)
        old_net_total = to_int(old_eod.sub_total)

        # NEW totals
        new_sales_total = sum(li.unit_price for li in tx.line_items if not li.is_return)
        new_returns_total = sum(abs(li.unit_price) for li in tx.line_items if li.is_return)
        new_net_total = new_sales_total - new_returns_total

        if old_sales_total != new_sales_total:
            print(f"Sales mismatch Ticket {ticket.ticket_number}: OLD={old_sales_total} NEW={new_sales_total}")
            mismatches += 1

        if old_returns_total != new_returns_total:
            print(f"Returns mismatch Ticket {ticket.ticket_number}: OLD={old_returns_total} NEW={new_returns_total}")
            mismatches += 1

        if old_net_total != new_net_total:
            print(f"Net total mismatch Ticket {ticket.ticket_number}: OLD={old_net_total} NEW={new_net_total}")
            mismatches += 1

    print("\n✅ Validation complete.")
    print(f"Total mismatches: {mismatches}")

    
    
# ---------------------------------
# RUN MIGRATION
# ---------------------------------

if __name__ == "__main__":
    migrate_users()
    migrate_deductions()
    migrate_eods_to_tickets_and_transactions()
    validate_migration()
    print("Migration completed.")