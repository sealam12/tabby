from tabby.fields import *
from tabby.adapters import Connector

class Model:
    def __init__(self, **kwargs):
        self._fields = []
        self._fields_dict = {}
        for k, v in self.__class__.__dict__.items():
            if not isinstance(v, Field): continue
            setattr(self, f"_field_{k}", v)
            self._fields.append(k)
            self._fields_dict[k] = v
        
        self._table = self.__class__.__name__.lower()
        for k, v in kwargs.items():
            # Turn integer id field for foreign keys into a class object of it's type
            if isinstance(self._fields_dict[k], ForeignKey) and v != None:
                setattr(self, k, Connector.adapter.get(self._fields_dict[k].reference_class, id=v))
                                
            setattr(self, k, v)
    
    def get_fields(self):
        fields = {}
        for k, v in self.__dict__.items():
            if not isinstance(self._fields_dict[k], Field): continue
            fields[k] = v
        
        return fields
    
    # Save any changes made to the model class
    def save(self):
        Connector.save(self)
    
    # Fetches the list of columns specified by the class in the definition
    @classmethod
    def get_fields(cls):
        fields = {}
        
        for k, v in cls.__dict__.items():
            if not isinstance(v, Field): continue
            fields[k] = v
        
        return fields
    
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

class User(Model):
    id = IntegerField(primary_key=True)
    username = StringField()
    password = StringField()