from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.models import Ticket, LineItem, Transaction, Deduction, User, Location
from app.extensions import db
from datetime import datetime
from sqlalchemy.orm import selectinload

reader = Blueprint("reader", __name__)


