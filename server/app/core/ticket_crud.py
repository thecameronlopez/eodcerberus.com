from flask import request, jsonify, current_app
from .crud_engine import CRUDEngine
from app.models import Ticket, Transaction, LineItem, Tender, SalesDay, SalesCategory, PaymentType
from app.schemas import ticket_create_schema, ticket_schema
from app.extensions import db
from app.services.allocations import allocate_tender_to_line_items
from datetime import datetime, timezone
from app.utils.timezone import to_business_date
from app.models import User, Location
from app.utils.tools import finalize_ticket
from marshmallow import ValidationError as MarshallowValidationError
from app.handlers.errors.domain import ConflictError, NotFoundError
from app.handlers.errors.validation import ValidationError as AppValidationError
from sqlalchemy.exc import IntegrityError

class TicketCRUDEngine(CRUDEngine):
    def create(self):
        """  
        JSON PAYLOAD EXAMPLE:
        {
            ticket_number: 1234, -> int
            ticket_date: 2026-01-01, -> str
            user_id: 1, -> int
            location_id: 1, -> int
            transaction_type: SALE, -> enum str
            line_items: [
                {
                    sales_category_id: 1, -> int
                    unit_price: 50000, -> int
                    quantity: 1, -> int                
                }, -> dict
            ], -> list
            tenders: [
                {
                    amount: 50000, -> int
                    payment_type_id: 1, -> int    
                }, -> dict    
            ], -> list
        }
        """
        try:
            data = ticket_create_schema.load(request.get_json())
        except MarshallowValidationError as e:
            raise AppValidationError(e.messages)
        
        #---------- Initialize meta data ------------
        user = db.session.get(User, data["user_id"])
        if not user:
            raise NotFoundError("User not found.")
        
        location = db.session.get(Location, data["location_id"])
        if not location:
            raise NotFoundError("Location not found.")
        
        #-------------- format date -----------------
        ticket_date = data["ticket_date"]
        
        
        #-------------- create sales day if not one --------------
        existing_sales_day = (
            db.session.query(SalesDay)
            .filter_by(
                user_id=user.id,
                location_id=location.id,
                status="open",
            )
            .order_by(SalesDay.opened_at.desc())
            .first()
        )
        if existing_sales_day and to_business_date(existing_sales_day.opened_at) == ticket_date:
            sales_day = existing_sales_day
        else:
            sales_day = SalesDay(
                user_id=user.id,
                location_id=location.id,
                opened_at=datetime.now(timezone.utc),
            )
            
        existing_ticket = db.session.query(Ticket).filter_by(ticket_number=data["ticket_number"]).first()
        if existing_ticket:
            raise ConflictError(f"Ticket number {existing_ticket.ticket_number} already used")
        ticket = Ticket(
            ticket_number=data["ticket_number"],
            ticket_date=ticket_date,
            location_id=location.id,
            user_id=user.id
        )
        sales_day.tickets.append(ticket)
            
        transaction = Transaction(
            ticket_id=ticket.id,
            user_id=user.id,
            location_id=location.id,
            posted_at=ticket_date,
            transaction_type=data["transaction_type"]
        )
        ticket.transactions.append(transaction)
        
        line_items = []
        for li in data["line_items"]:
            sales_category = db.session.get(SalesCategory, li["sales_category_id"])
            if not sales_category:
                raise NotFoundError(f"SalesCategory {li['sales_category_id']} not found.")
            line_item = LineItem(
                sales_category_id=sales_category.id,
                unit_price=li["unit_price"],
                quantity=li["quantity"],
                taxable=sales_category.taxable,
                taxability_source="CATEGORY_DEFAULT",
                tax_rate=location.current_tax_rate
            )
            line_items.append(line_item)
            transaction.line_items.append(line_item)
            
        tenders = []
        for t in data["tenders"]:
            payment_type = db.session.get(PaymentType, t["payment_type_id"])
            if not payment_type:
                raise NotFoundError(f"PaymentType {t['payment_type_id']} not found.")
            tender = Tender(
                payment_type_id=payment_type.id,
                amount=t["amount"]
            )
            tenders.append(tender)
            transaction.tenders.append(tender)
            
        for t in tenders:
            allocations = allocate_tender_to_line_items(transaction, t)
            t.allocations.extend(allocations)
        
        finalize_ticket(ticket)
        
        try:
            db.session.add(sales_day)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            raise ConflictError("User already has an open sales day.") from e
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"[TICKET SUBMISSION ERROR]: {e}")
            raise

        current_app.logger.info(f"[NEW TICKET CREATED]: {user.first_name} {user.last_name} created a new ticket: {ticket.ticket_number}")
        return jsonify(
            success=True,
            message="Ticket created successfully!",
            ticket=ticket_schema.dump(ticket)
        ), 201
       
