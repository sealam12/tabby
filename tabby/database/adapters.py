from tabby.database.connection import db
from tabby.utils.config import Settings
from tabby.models.fields import *
import inspect

class SQLiteMigration:
    def ensure_table(self):
        db.execute("CREATE TABLE IF NOT EXISTS _migrations (table_name TEXT, migration_id INTEGER, applied BOOLEAN)")
        db.commit()
        
    def fetch_migrations(self, cls):
        migrations = db.execute("SELECT migration_id, table_name, applied FROM _migrations WHERE table_name=?", (cls.get_table(), )).fetchall()
        return migrations
    
    def new_table(self, cls):
        fields = cls.get_fields()
        fieldstrs = []
        for key, field in fields.items():
            fieldstrs.append(f"{key} {" ".join([constr for constr in field.constraints])}")
        
        command = f"CREATE TABLE IF NOT EXISTS {cls.get_table()} ({", ".join(fieldstrs)})"
        return command

    def new_field(self, cls, key, field):
        constraints = [ constr for constr in field["constraints"]]
        fieldstr = f"{key} {field["type"]} {" ".join(constraints)}"
        
        command = f"ALTER TABLE {cls.get_table()} ADD COLUMN {fieldstr}"
        return command

    def remove_field(self, cls, key):
        command = f"ALTER TABLE {cls.get_table()} DROP COLUMN {key}"
        return command
    
    def rename_field(self, cls, key_old, key_new):
        command = f"ALTER TABLE {cls.get_table()} RENAME COLUMN {key_old} TO {key_new}"
        return command
    
    def transfer_fields(self, cls, key_old, key_new):
        command = f"UPDATE {cls.get_table()} SET {key_old}={key_new}"
        return command

    def save_migration(self, table, id):
        command = f"INSERT INTO _migrations (migration_id, table_name, applied) VALUES ({id}, \"{table}\", FALSE)"
        return command

    def set_migration_applied(self, table, id):
        command = f"UPDATE _migrations SET applied=TRUE WHERE table_name=\"{table}\", migration_id={id}"

class SQLite:
    # Configure the SQLite session as needed
    def __init__(self):
        self.migrations = SQLiteMigration()
        db.execute("PRAGMA foreign_keys = ON")
        
    def get(self, cls, **kwargs):
        columns = cls.get_columns()
        table_name = cls.__name__.lower()
        columns_text = ", ".join(columns)
        
        kwargs_list = [f"{k}={v}" for k, v in kwargs.items()]
        kwargs_text = ", ".join(kwargs_list)
        model_data = db.execute(f"SELECT {columns_text} FROM {table_name} WHERE ({kwargs_text})").fetchone()
        
        new_model_kwargs = {}
        for index, value in enumerate(model_data):
            col = columns[index]
            new_model_kwargs[col] = value
        
        # Initialize a class for the model retrieved with columns & values
        model = cls(**new_model_kwargs)
        return model
    
    def filter(self, cls, **kwargs):
        columns = cls.get_columns()
        table_name = cls.__name__.lower()
        columns_text = ", ".join(columns)
        
        kwargs_list = [f"{k}={v}" for k, v in kwargs.items() if not isinstance(v, str)]
        kwargs_list.extend([f"{k}=\"{v}\"" for k, v in kwargs.items() if isinstance(v, str)])
        kwargs_text = ", ".join(kwargs_list)
        model_data_all = db.execute(f"SELECT {columns_text} FROM {table_name} WHERE ({kwargs_text})").fetchall()
        
        models = []
        for model_data in model_data_all:
            new_model_kwargs = {}
            for index, value in enumerate(model_data):
                col = columns[index]
                new_model_kwargs[col] = value
            
            # Initialize a class for the model retrieved with columns & values
            model = cls(**new_model_kwargs)
            models.append(model)
            
        return models

    def all(self, cls, **kwargs):
        columns = cls.get_columns()
        table_name = cls.__name__.lower()
        columns_text = ", ".join(columns)
        model_data_all = db.execute(f"SELECT {columns_text} FROM {table_name}").fetchall()
        
        models = []
        for model_data in model_data_all:
            new_model_kwargs = {}
            for index, value in enumerate(model_data):
                col = columns[index]
                new_model_kwargs[col] = value
            
            # Initialize a class for the model retrieved with columns & values
            model = cls(**new_model_kwargs)
            models.append(model)
            
        return models

    def save(self, cls, **kwargs):
        columns = cls.get_fields()
        columns_set_list = []
        for k, v in columns.items():
            if isinstance(v, str): v = f"\"{v}\""
            if isinstance(cls._fields_dict[k], ForeignKey): v = v.id
            columns_set_list.append(f"{k}={v}")
        columns_set_text = ", ".join(columns_set_list)
        db.execute(f"UPDATE {cls._table} SET {columns_set_text} WHERE id={cls.id}")
        db.commit()

class AdapterManager:
    adapter = getattr(inspect.getmodule(inspect.currentframe()), Settings.DATABASE_ADAPTER)()
    migrations = adapter.migrations
        
    def get(self, cls, **kwargs):
        return self.adapter.get(cls, **kwargs)
    
    def filter(self, cls, **kwargs):
        return self.adapter.filter(cls, **kwargs)
    
    def all(self, cls, **kwargs):
        return self.adapter.all(cls, **kwargs)
    
    def save(self, cls, **kwargs):
        return self.adapter.save(cls, **kwargs)

Connector = AdapterManager()