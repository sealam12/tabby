import os, sys, json
from tabby.connection import db
from tabby.adapters import Connector
from tabby.model import Model
from tabby import serialize
from tabby import log

class MigrationManager:
    def __init__(self, models_path, migrations_path):
        self.models_path = models_path
        self.migrations_path = migrations_path
        Connector.migrations.ensure_table()
    
    def scan_file(self, file):
        module_name = file[0:-3]
        models = []
        module = __import__("tabby.model", fromlist="model")
        for obj in module.__dict__.values():
            #print(obj, isinstance(obj, type))
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
            migration_name = f"{cls.get_table()}_{migration_id:04}"
            self.save_migration(data, migration_name)
            
            save_cmd = Connector.migrations.save_migration(cls.get_table(), migration_id)
            db.execute(save_cmd)
            
            log.success(f"Saved migration to {self.migrations_path}/{migration_name}.json")
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
            
            migration_name = f"{cls.get_table()}_{migration_id:04}"
            self.save_migration(data, migration_name)
            
            save_cmd = Connector.migrations.save_migration(cls.get_table(), migration_id)
            db.execute(save_cmd)
        
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
            log.log(f"Applying migration {migration_name}...")
            # Execute command specified by migration file
            for cmd in migration_data["cmds"]: db.execute(cmd)
            # Set migration status to applied in the database
            Connector.migrations.set_migration_applied(migration[1], migration[0])
        log.success(f"Successfully applied {len(unapplied_migrations)} migrations.")
    
    def applymigrations(self):
        models = self.scan()
        for model in models:
            self.apply_class_migrations(model)
            
    
if __name__ == "__main__":
    m = MigrationManager("model.py", "migrations")
    m.makemigrations()
    m.applymigrations()