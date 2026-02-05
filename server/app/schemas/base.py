from marshmallow import Schema, pre_load


class BaseSchema(Schema):
    class Meta:
        strip_strings = True
        strip_exclude = set()
        
    @pre_load
    def strip_strings(self, data, **kwargs):
        if not isinstance(data, dict):
            return data
        
        if not getattr(self.Meta, "strip_strings", False):
            return data
        
        exclude = getattr(self.Meta, "strip_exclude", set())
        
        return {
            k: v.strip() if isinstance(v, str) and k not in exclude else v 
            for k, v in data.items()
        }
        
    
    
class UpdateSchema(BaseSchema):
    def load(self, data, *args, **kwargs):
        kwargs.setdefault('partial', True)
        return super().load(data, *args, **kwargs)