from flask import current_app
from app.extensions import db


def commit_or_rollback():
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[DB ERROR]: {e}")
        raise