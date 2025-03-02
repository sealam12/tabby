from tabby.model import *
from tabby.fields import *
import json

def serialize_field(cls):
    data = {
        "type": cls.sql_type,
        "constraints": cls.constraints
    }
    
    return data

def serialize_model(cls):
    data = {
        "fields": {k: serialize_field(field) for k, field in cls.get_fields().items()}
    }
    
    return data