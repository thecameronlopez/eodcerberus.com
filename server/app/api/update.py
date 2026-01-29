from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.models import Ticket, LineItem, Deduction, User, Location, TaxRate, Transaction
from app.extensions import db
from datetime import datetime, timedelta, date
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.utils.tools import to_int

updator = Blueprint("update", __name__)

