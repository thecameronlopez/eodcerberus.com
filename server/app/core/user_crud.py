from flask import request
from app.core.crud_engine import CRUDEngine
from app.extensions import db, bcrypt
from app.handlers.errors.validation import ValidationError as AppValidationError
from app.models import Department, Location, User
from app.schemas import user_register_schema
from app.utils.responses import success


class UserCRUDEngine(CRUDEngine):
    def create(self):
        data = user_register_schema.load(self._get_json_payload())

        department_name = (data.get("department") or "").strip()
        location_code = (data.get("location_code") or "").strip()

        if not department_name:
            raise AppValidationError({"department": ["Department is required."]})
        if not location_code:
            raise AppValidationError({"location_code": ["Location code is required."]})

        department = (
            db.session.query(Department)
            .filter(Department.name.ilike(department_name))
            .first()
        )
        if not department:
            raise AppValidationError({"department": [f"Unknown department '{department_name}'."]})

        location = (
            db.session.query(Location)
            .filter(Location.code.ilike(location_code))
            .first()
        )
        if not location:
            raise AppValidationError({"location_code": [f"Unknown location '{location_code}'."]})

        user = User(
            email=data["email"].lower(),
            first_name=data["first_name"].title(),
            last_name=data["last_name"].title(),
            department=department,
            location=location,
            is_admin=bool(data.get("is_admin", False)),
            password_hash=bcrypt.generate_password_hash(data["pw"]).decode("utf-8"),
        )

        db.session.add(user)
        db.session.commit()

        return success(
            "User created",
            {self.model.__name__.lower(): self.read_schema.dump(user)},
            201,
        )

    @staticmethod
    def _get_json_payload():
        return request.get_json()
