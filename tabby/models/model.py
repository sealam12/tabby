from tabby.models.field import Field
from tabby.models.fields import StringField

class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        # Iterate over the attributes to find fields
        for key, value in attrs.copy().items():
            if isinstance(value, Field):
                # Create a property for the field
                attrs[key] = property(
                    fget=lambda self, key=key: getattr(self, f"_{key}").value,
                    fset=lambda self, value, key=key: setattr(getattr(self, f"_{key}"), 'value', value)
                )
                # Initialize the field
                attrs[f"_{key}"] = value
        return super().__new__(cls, name, bases, attrs)
    

class Model(metaclass=ModelMeta):
    def delete(self):
        pass

    def save(self):
        pass
    
    @classmethod
    def get(self, **kwargs):
        for k, v in kwargs.items():
            print(k, v)
    
    @classmethod
    def filter(self, **kwargs):
        pass

    @classmethod
    def create(cls, **kwargs):
        # Create an instance of the subclass
        instance = cls()
        
        # Iterate over the provided keyword arguments
        for field, value in kwargs.items():
            if hasattr(instance, field):
                # Use the property setter to set the field value
                setattr(instance, field, value)  # This will call the property setter
            else:
                raise AttributeError(f"{cls.__name__} has no field '{field}'")
        
        return instance
    
class TestObj(Model):
    field = StringField()

e = TestObj.create(field="Test")
e = TestObj.get(id=5)