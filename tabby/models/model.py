from tabby.models.fields import *
from tabby.utils import errors
from tabby.database.adapters import Connector

class ModelMeta(type):
    def __new__(cls, name, bases, dct):
        model = super().__new__(cls, name, bases, dct)
        
        model.id = IntegerField(primary_key=True)
        
        model._table = name.lower()
        
        model._model_fields_list = []
        model._model_fields_dict = {}
        for k, v in model.__dict__.items():
            if not isinstance(v, Field): continue
            
            model._model_fields_list.append(k)
            model._model_fields_dict[k] = v
        
        return model

class Model(metaclass=ModelMeta):
    def __init__(self, **kwargs):
        self._instance_fields_list = []
        self._instance_fields_dict = {}
        
        for k, v in kwargs.items():
            if not isinstance(self._model_fields_dict[k], Field): continue
            
            self._instance_fields_list.append(k)
            self._instance_fields_dict[k] = v
                     
            setattr(self, k, v)
            
    def __setattr__(self, name, value):
        if name in self._model_fields_list:
            field = self._model_fields_dict[name]
            self._instance_fields_dict[name] = value
            if not isinstance(value, field.python_type):
                raise errors.InvalidFieldInputError(f"Invalid field input, input for {field.__class__.__name__} should be of type {field.python_type} but was of type {type(value)}")
        
        super(Model, self).__setattr__(name, value)
    
    # Save any changes made to the model class
    def save(self):
        Connector.save(self)
    
    @classmethod
    def get(cls, **kwargs):
        return Connector.get(cls, **kwargs)

    @classmethod
    def filter(cls, **kwargs):
        return Connector.filter(cls, **kwargs)
    
    @classmethod
    def all(cls, **kwargs):
        return Connector.all(cls, **kwargs)
    
    @classmethod
    def get_table(cls):
        return cls.__name__.lower()