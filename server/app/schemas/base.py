from marshmallow import Schema, pre_load


class BaseSchema(Schema):
    @pre_load
    def strip_strings(self, data, **kwargs):
        if isinstance(data, dict):
            return {
                k: v.strip() if isinstance(v, str) else v 
                for k, v in data.items()
            }
        
        return data