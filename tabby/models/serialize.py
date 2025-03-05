from tabby.models.model import *
from tabby.models.fields import *
import json

def serialize_field(cls):
    data = {
        "type": cls.sql_type,
        "constraints": cls.constraints
    }
    
    return data

def serialize_model(cls):
    data = {
        "fields": {k: serialize_field(field) for k, field in cls._model_fields_dict.items()}
    }
    
    return data