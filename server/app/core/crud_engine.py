from flask import request
from app.extensions import db
from app.utils.responses import success
from app.handlers.errors.domain import NotFoundError, ConflictError
from sqlalchemy.exc import IntegrityError


class CRUDEngine:
    def __init__(self, model, read_schema, create_schema=None, update_schema=None):
        self.model = model
        self.read_schema = read_schema
        self.create_schema = create_schema
        self.update_schema = update_schema
        
    
    def get(self, id):
        instance = db.session.get(self.model, id)
        
        if not instance:
            raise NotFoundError(f"{self.model.__name__} not found")
        
        
        expand = request.args.get("expand", "false").lower() in ("1", "true")
        
        schema = self.read_schema
        if expand and hasattr(self, "detail_schema"):
            schema = self.detail_schema        
        
        return success(data={
            self.model.__name__.lower(): schema.dump(instance)
        })
        
        
    def list(self):
        items = db.session.query(self.model).all()
        plural = self._plural_key()
        return success(data={
            plural: self.read_schema.dump(items, many=True)
        })

    def _plural_key(self):
        if hasattr(self.model, "__plural__"):
            return getattr(self.model, "__plural__")

        name = self.model.__name__.lower()
        if name.endswith("y") and len(name) > 1 and name[-2] not in "aeiou":
            return name[:-1] + "ies"
        if name.endswith(("s", "x", "z", "ch", "sh")):
            return name + "es"
        return name + "s"
        
    
    def create(self):
        data = request.get_json()

        instance = self.create_schema.load(data)

        if isinstance(instance, dict):
            instance = self.model(**instance)
        
        try:
            db.session.add(instance)
            db.session.commit()
        except IntegrityError as err:
            db.session.rollback()
            raise ConflictError(f"{self.model.__name__} conflicts with existing data.") from err
        except Exception:
            db.session.rollback()
            raise
        
        return success(
            f"{self.model.__name__} created",
            {self.model.__name__.lower(): self.read_schema.dump(instance)},
            201
        )
        
        
    def update(self, id):
        instance = db.session.get(self.model, id)
        
        if not instance:
            raise NotFoundError(f"{self.model.__name__} not found")
        
        data = request.get_json()
        
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
        instance = db.session.get(self.model, id)
        
        if not instance:
            raise NotFoundError(f"{self.model.__name__} not found")
        
        try:
            db.session.delete(instance)
            db.session.commit()
        except IntegrityError as err:
            db.session.rollback()
            raise ConflictError(f"{self.model.__name__} cannot be deleted due to related data.") from err
        except Exception:
            db.session.rollback()
            raise
        
        return success(f"{self.model.__name__} deleted")
