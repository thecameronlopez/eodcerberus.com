from flask import request, current_app
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError as MarshmallowValidationError

from app.extensions import db
from app.core.crud_engine import CRUDEngine
from app.models import Transaction, Ticket, User, Location, LineItem, Tender, SalesCategory, PaymentType
from app.schemas import transaction_create_schema, transaction_schema
from app.services.allocations import allocate_tender_to_line_items
from app.utils.responses import success
from app.utils.tools import finalize_transaction, finalize_ticket
from app.handlers.errors.domain import NotFoundError, ConflictError
from app.handlers.errors.validation import ValidationError as AppValidationError


class TransactionCRUDEngine(CRUDEngine):
    def create(self):
        """
        JSON PAYLOAD EXAMPLE:
        {
            ticket_id: 1,
            user_id: 1,
            location_id: 1,
            posted_at: 2026-02-01,
            transaction_type: "sale",
            line_items: [
                {
                    sales_category_id: 1,
                    unit_price: 50000,
                    quantity: 1
                }
            ],
            tenders: [
                {
                    payment_type_id: 1,
                    amount: 50000
                }
            ]
        }
        """
        try:
            data = transaction_create_schema.load(request.get_json() or {})
        except MarshmallowValidationError as err:
            raise AppValidationError(err.messages)

        ticket = db.session.get(Ticket, data["ticket_id"])
        if not ticket:
            raise NotFoundError("Ticket not found.")

        user = db.session.get(User, data["user_id"])
        if not user:
            raise NotFoundError("User not found.")

        location = db.session.get(Location, data["location_id"])
        if not location:
            raise NotFoundError("Location not found.")

        transaction = Transaction(
            ticket_id=ticket.id,
            user_id=user.id,
            location_id=location.id,
            posted_at=data["posted_at"],
            transaction_type=data["transaction_type"],
        )
        ticket.transactions.append(transaction)

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
                tax_rate=location.current_tax_rate,
            )
            transaction.line_items.append(line_item)

        tenders = []
        for t in data["tenders"]:
            payment_type = db.session.get(PaymentType, t["payment_type_id"])
            if not payment_type:
                raise NotFoundError(f"PaymentType {t['payment_type_id']} not found.")

            tender = Tender(
                payment_type_id=payment_type.id,
                amount=t["amount"],
            )
            tenders.append(tender)
            transaction.tenders.append(tender)

        for tender in tenders:
            allocations = allocate_tender_to_line_items(transaction, tender)
            tender.allocations.extend(allocations)

        finalize_transaction(transaction)
        finalize_ticket(ticket)

        try:
            db.session.add(transaction)
            db.session.commit()
        except IntegrityError as err:
            db.session.rollback()
            raise ConflictError("Transaction conflicts with existing data.") from err
        except Exception as err:
            db.session.rollback()
            current_app.logger.error(f"[TRANSACTION CREATE ERROR]: {err}")
            raise

        current_app.logger.info(
            "[NEW TRANSACTION CREATED]: user=%s ticket=%s transaction=%s",
            user.id,
            ticket.ticket_number,
            transaction.id,
        )
        return success(
            "Transaction created",
            {"transaction": transaction_schema.dump(transaction)},
            201,
        )
