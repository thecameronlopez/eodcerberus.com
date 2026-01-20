# delete_routes.py
from flask import Blueprint, jsonify, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Ticket, Deduction, Transaction, LineItem, User

deleter = Blueprint("delete", __name__)

#-------------------
# DELETE TICKET
#-------------------
@deleter.route("/ticket/<int:ticket_id>", methods=["DELETE"])
@login_required
def delete_ticket(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify(success=False, message="Ticket not found"), 404

    try:
        db.session.delete(ticket)
        db.session.commit()
        current_app.logger.info(f"[TICKET DELETE] {current_user.first_name} deleted ticket {ticket_id}")
        return jsonify(success=True, message="Ticket deleted successfully."), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[TICKET DELETE ERROR] {e}")
        return jsonify(success=False, message="Error deleting ticket."), 500
    

#-------------------
# DELETE TRANSACTION
#-------------------
@deleter.route("/transaction/<int:transaction_id>", methods=["DELETE"])
@login_required
def delete_transaction(transaction_id):
    transaction = db.session.get(Transaction, transaction_id)
    if not transaction:
        return jsonify(success=False, message="Transaction not found"), 404

    try:
        ticket = transaction.ticket
        db.session.delete(transaction)
        if ticket:
            ticket.compute_total()
            
        db.session.commit()
        current_app.logger.info(f"[TRANSACTION DELETED] {current_user.first_name} deleted transaction {transaction_id}")
        return jsonify(success=True, message="Transaction deleted successfully."), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[TRANSACTION DELETE ERROR] {e}")
        return jsonify(success=False, message="Error deleting transaction."), 500


#-------------------
# DELETE LINE ITEM
#-------------------
@deleter.route("/line_item/<int:line_item_id>", methods=["DELETE"])
@login_required
def delete_line_item(line_item_id):
    line_item = db.session.get(LineItem, line_item_id)
    if not line_item:
        return jsonify(success=False, message="Line item not found"), 404

    # Optional: prevent deleting if ticket/transaction date is finalized
    # e.g., if line_item.transaction.posted_date < some_cutoff_date:
    #     return jsonify(success=False, message="Cannot delete line item for closed date"), 403

    try:
        transaction = line_item.transaction
        ticket = transaction.ticket if transaction else None
        
        transaction_id = line_item.transaction_id
        db.session.delete(line_item)
        
        if transaction:
            transaction.compute_total()
        if ticket:
            ticket.compute_total()
        
        db.session.commit()
        current_app.logger.info(
            f"[LINE ITEM DELETE] {current_user.first_name} deleted line item {line_item_id} from transaction {transaction_id}"
        )
        return jsonify(success=True, message="Line item deleted successfully."), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[LINE ITEM DELETE ERROR]: {e}")
        return jsonify(success=False, message="Error deleting line item."), 500



#-------------------
# DELETE DEDUCTION
#-------------------
@deleter.route("/deduction/<int:deduction_id>", methods=["DELETE"])
@login_required
def delete_deduction(deduction_id):
    deduction = db.session.get(Deduction, deduction_id)
    if not deduction:
        return jsonify(success=False, message="Deduction not found"), 404

    try:
        db.session.delete(deduction)
        db.session.commit()
        current_app.logger.info(f"[DEDUCTION DELETE] {current_user.first_name} deleted deduction {deduction_id}")
        return jsonify(success=True, message="Deduction deleted successfully."), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[DEDUCTION DELETE ERROR] {e}")
        return jsonify(success=False, message="Error deleting deduction."), 500


@deleter.route("/user/<int:user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return jsonify(success=False, message="Unauthorized"), 403

    user = db.session.get(User, user_id)
    if not user:
        return jsonify(success=False, message="User not found"), 404

    try:
        db.session.delete(user)
        db.session.commit()
        current_app.logger.info(f"[USER DELETE] {current_user.first_name} deleted user {user_id}")
        return jsonify(success=True, message="User deleted successfully."), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[USER DELETE ERROR] {e}")
        return jsonify(success=False, message="Error deleting user."), 500