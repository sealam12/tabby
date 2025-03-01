from tabby.connection import db
from tabby.field import *

class Model:
    
    def __init__(self, **kwargs):
        self._table = self.__class__.__name__.lower()
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    # Save any changes made to the model class
    def save(self):
        columns = self.get_columns_dict()
        columns_set_list = []
        for k, v in columns.items():
            if isinstance(v, str): v = f"\"{v}\""
            columns_set_list.append(f"{k}={v}")
        columns_set_text = ", ".join(columns_set_list)
        
        sql = f"UPDATE {self._table} SET {columns_set_text} WHERE id={self.id}"
        db.execute(sql)
        db.commit()
    
    # Returns a dict of the columns and their values in a Model class
    # Used primarily for saving models
    def get_columns_dict(self):
        columns = {}
        for k, v in self.__dict__.items():
            if k[0] == "_": continue
            columns[k] = v
        
        return columns
    
    # Fetches the list of columns specified by the class in the definition
    @classmethod
    def get_columns(cls, *, types=False, constraints=False):
        columns = []
        
        for k, v in cls.__dict__.items():
            if not isinstance(v, Field): continue
            column_text = str(k)
            if types: column_text += f" {v.sql_type}"
            if constraints: column_text += f" {' '.join(v.constraints)}"
            
            columns.append(column_text)
        
        return columns
    
    # Fetches model from database based off of queries / constraints
    # provided through KWARGS
    @classmethod
    def get(cls, **kwargs):
        columns = cls.get_columns()
        table_name = cls.__name__.lower()
        columns_text = ", ".join(columns)
        
        kwargs_list = [f"{k}={v}" for k, v in kwargs.items()]
        kwargs_text = ", ".join(kwargs_list)
        sql = f"SELECT {columns_text} FROM {table_name} WHERE ({kwargs_text})"
        
        model_data = db.execute(sql).fetchone()
        new_model_kwargs = {}
        for index, value in enumerate(model_data):
            col = columns[index]
            new_model_kwargs[col] = value
        
        # Initialize a class for the model retrieved with columns & values
        model = cls(**new_model_kwargs)
        return model

class User(Model):
    id = IntegerField(primary_key=True)
    username = StringField()
    password = StringField()
    test_field = StringField()