from flask import request
from flask_login import current_user
from app.core.crud_engine import CRUDEngine
from app.extensions import db, bcrypt
from app.handlers.errors.validation import ValidationError as AppValidationError
from app.handlers.errors.domain import ConflictError, NotFoundError, PermissionDenied
from app.models import Department, Location, User
from app.schemas import user_register_schema
from app.utils.responses import success
from sqlalchemy.exc import IntegrityError


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
            is_admin=bool(data.get("is_admin", False)) if current_user.is_authenticated and current_user.is_admin else False,
            password_hash=bcrypt.generate_password_hash(data["pw"]).decode("utf-8"),
        )

        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError as err:
            db.session.rollback()
            raise ConflictError(f"Email '{data['email'].lower()}' is already in use.") from err

        return success(
            "User created",
            {self.model.__name__.lower(): self.read_schema.dump(user)},
            201,
        )

    def update(self, id):
        instance = db.session.get(self.model, id)
        if not instance:
            raise NotFoundError(f"{self.model.__name__} not found")

        is_self = current_user.is_authenticated and current_user.id == id
        is_admin = current_user.is_authenticated and getattr(current_user, "is_admin", False)
        if not (is_self or is_admin):
            raise PermissionDenied("You can only update your own user record.")

        data = self._get_json_payload() or {}
        if not is_admin:
            blocked = {"is_admin", "terminated"}
            if blocked.intersection(data.keys()):
                raise PermissionDenied("Only admins can modify admin/termination fields.")

        instance = self.update_schema.load(
            data,
            instance=instance,
            partial=True
        )

        try:
            db.session.commit()
        except IntegrityError as err:
            db.session.rollback()
            raise ConflictError(f"{self.model.__name__} conflicts with existing data.") from err
        except Exception:
            db.session.rollback()
            raise

        return success(
            f"{self.model.__name__} updated",
            {self.model.__name__.lower(): self.read_schema.dump(instance)}
        )

    def delete(self, id):
        raise PermissionDenied("User deletion is disabled.")

    @staticmethod
    def _get_json_payload():
        return request.get_json()
