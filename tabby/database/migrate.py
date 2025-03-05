import os, sys, json
from tabby.database.connection import db
from tabby.database.adapters import Connector
from tabby.models.model import Model
from tabby.models import serialize
from tabby.utils import log, errors

class MigrationManager:
    def __init__(self, models_path, migrations_path):
        self.models_path = models_path
        self.migrations_path = migrations_path
        Connector.migrations.ensure_table()
        os.makedirs(migrations_path, exist_ok=True)
    
    def scan_file(self, file):
        # Get the directory of the file
        directory = os.path.dirname(file)
        
        # Extract the module name without the .py extension
        module_name = os.path.splitext(os.path.basename(file))[0]
        
        # Append the directory to sys.path
        if directory not in sys.path:
            sys.path.append(directory)
        
        # Import the module
        module = __import__(module_name)
        
        models = []
        for obj in module.__dict__.values():
            if isinstance(obj, type) and issubclass(obj, Model) and obj != Model: 
                models.append(obj)
        
        return models
        
    def scan(self):
        path = self.models_path
        models = []
        if os.path.isdir(path):
            files = os.scandir(self.models_path)
        else:
            models = self.scan_file(self.models_path)
        return models

    def save_migration(self, data, name):
        with open(f"{self.migrations_path}/{name}.json", "w") as file:
            json.dump(data, file, indent=4)
    
    def load_migration(self, name):
        with open(f"{self.migrations_path}/{name}.json", "r") as file:
            data = json.load(file)
        return data

    def make_class_migrations(self, cls):
        log.log("Checking for previous migrations...")
        previous_migrations = Connector.migrations.fetch_migrations(cls)
        log.log(f"Found {len(previous_migrations)} previous migrations.")
        # unapplied_migrations = [m for m in previous_migrations if bool(m[2])]
        
        current_schema = serialize.serialize_model(cls)
            
        if len(previous_migrations) == 0:
            migration_id = 0
            log.error("No previous migrations found.")
            
            data = {
                "cmds": [],
                "schema": current_schema
            }
            
            log.log("Saving migration...")
            data['cmds'].append(Connector.migrations.new_table(cls))
            migration_name = f"{cls._table}_{migration_id:04}"
            self.save_migration(data, migration_name)
            
            save_cmd = Connector.migrations.save_migration(cls._table, migration_id)
            db.execute(save_cmd)
            
            log.success(f"Saved migration to {self.migrations_path}{migration_name}.json")
        else:
            most_recent = sorted(previous_migrations)[-1]
            migration_id = len(previous_migrations)
            
            data = {
                "cmds": [],
                "schema": current_schema
            }
            
            old_schema = self.load_migration(f"{most_recent[1]}_{most_recent[0]:04}")["schema"]
            log.log("Checking for schema changes...")
            if old_schema == current_schema:
                log.error("No changes since last migration.")
                return
            
            # Check for fields being added
            for key, field in current_schema["fields"].items():
                if key not in old_schema["fields"].keys():
                    log.log(f"Found new field {key}")
                    
                    found = False
                    for constr in field["constraints"]:
                        if "DEFAULT" in constr:
                            found = True
                    if not found and "NOT NULL" in field["constraints"]:
                        raise errors.NotNullConstraintError(f"Cannot add new field {key} to {cls._table} with NOT NULL constraint which has no default value")
                        
                    data["cmds"].append(Connector.migrations.new_field(cls, key, field))
            
            # Check for fields being removed
            for key, field in old_schema["fields"].items():
                if key not in current_schema["fields"].keys():
                    log.log(f"Field {key} not in new schema")
                    data["cmds"].append(Connector.migrations.remove_field(cls, key))
            
            # Check for field constraints being changed
            for key, field in current_schema["fields"].items():
                if key not in old_schema["fields"].keys(): continue
                field2 = old_schema["fields"][key]
                if field["constraints"] != field2["constraints"]:
                    log.log(f"Found changed constraints on field {key}")
                    
                    data["cmds"].append(Connector.migrations.rename_field(cls, key, f"{key}_tmp"))
                    data["cmds"].append(Connector.migrations.new_field(cls, key, field))
                    data["cmds"].append(Connector.migrations.transfer_fields(cls, f"{key}_tmp", key))
                    data["cmds"].append(Connector.migrations.remove_field(cls, f"{key}_tmp"))
            
            log.log("Saving migration...")
            
            migration_name = f"{cls._table}_{migration_id:04}"
            self.save_migration(data, migration_name)
            
            save_cmd = Connector.migrations.save_migration(cls._table, migration_id)
            db.execute(save_cmd)
            
            log.success(f"Saved migration to {self.migrations_path}{migration_name}.json")
        
        db.commit()
    
    def makemigrations(self):
        models = self.scan()
        for model in models:
            self.make_class_migrations(model)
    
    def apply_class_migrations(self, cls):
        log.log("Checking for unapplied migrations...")
        previous_migrations = Connector.migrations.fetch_migrations(cls)
        unapplied_migrations = [m for m in previous_migrations if not bool(m[2])]
        log.log(f"Found {len(unapplied_migrations)} unapplied migrations.")
        
        for migration in unapplied_migrations:
            migration_name = f"{migration[1]}_{migration[0]:04}"
            # Load migration file and it's data
            migration_data = self.load_migration(f"{migration_name}")
            log.info(f"Applying migration {migration_name}...")
            # Execute command specified by migration file
            for cmd in migration_data["cmds"]: db.execute(cmd)
            # Set migration status to applied in the database
            Connector.migrations.set_migration_applied(migration[1], migration[0])
        log.success(f"Successfully applied {len(unapplied_migrations)} migrations.")
    
    def applymigrations(self):
        models = self.scan()
        for model in models:
            self.apply_class_migrations(model)