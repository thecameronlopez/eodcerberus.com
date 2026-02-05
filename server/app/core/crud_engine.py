from flask import request
from app.extensions import db
from app.utils.responses import success, error


class CRUDEngine:
    def __init__(self, model, read_schema, create_schema=None, update_schema=None):
        self.model = model
        self.read_schema = read_schema
        self.create_schema = create_schema
        self.update_schema = update_schema
        
    
    def get(self, id):
        instance = db.session.get(self.model, id)
        
        if not instance:
            return error(f"{self.model.__name__} not found", 404)
        
        
        return success(data={
            self.model.__name__.lower(): self.read_schema.dump(instance)
        })
        
        
    def list(self):
        items = db.session.query(self.model).all()
        
        return success(data={
            self.model.__name__.lower() + "s":
                self.read_schema.dump(items, many=True)
        })
        
    
    def create(self):
        data = request.get_json()
        
        instance = self.create_schema.load(data)
        
        db.session.add(instance)
        db.session.commit()
        
        return success(
            f"{self.model.__name__} created",
            {self.model.__name__.lower(): self.read_schema.dump(instance)},
            201
        )
        
        
    def update(self, id):
        instance = db.session.get(self.model, id)
        
        if not instance:
            return error(f"{self.model.__name__} nor found", 404)
        
        data = request.get_json()
        
        instance = self.update_schema.load(
            data,
            instance=instance,
            partial=True
        )
        
        db.session.commit()
        
        return success(
            f"{self.model.__name__} updated",
            {self.model.__name__.lower(): self.read_schema.dump(instance)}
        )
        
        
    def delete(self, id):
        instance = db.session.get(self.model, id)
        
        if not instance:
            return error(f"{self.model.__name__} not found", 404)
        
        db.session.delete(instance)
        db.session.commit()
        
        return success(f"{self.model.__name__} deleted")