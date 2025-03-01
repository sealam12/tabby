import os, sys, json
from tabby.connection import db
from tabby.model import Model
from tabby import log

class MigrationManager:
    def __init__(self, models_path, migrations_path):
        self.models_path = models_path
        self.migrations_path = migrations_path
    
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

    def ensure_migrations_table(self):
        db.execute("CREATE TABLE IF NOT EXISTS migrations(id INTEGER, model TEXT, name TEXT, applied BOOLEAN)")
    
    def make_class_migrations(self, cls):
        table_name = cls.__name__.lower()
        log.log("Collecting previous migrations..")
        sql = db.execute(f"SELECT id FROM migrations WHERE model=?", (table_name, )).fetchall()
        migration_id = len(sql)
        migration_name = f"{table_name}_{migration_id:04}"
        
        log.log(f"Fetching schema for [{table_name}]...")
        schema = cls.get_columns(types=True,constraints=True)
        if len(sql) == 0:
            log.info("No previous migrations, adding new table to migration...")
            schema_text = ", ".join(schema)
            sql_instruction = f"CREATE TABLE IF NOT EXISTS {table_name}({schema_text})"
        else:
            # Sorts the found ID's in the table and returns the largest ID
            most_recent_migration = sorted(sql)[-1][0]
            recent_file = f"{table_name}_{most_recent_migration:04}"
            
            # load the schema of the most recent migration
            log.log("Checking most recent migration for schema changes...")
            with open(f"{self.migrations_path}/{recent_file}.json", "r") as file:
                recent_migration = json.load(file)
            old_schema = recent_migration["schema"]
            
            if old_schema == schema:
                log.error("No schema changes since last migration.")
                return
        
            column_additions = []
            for column in schema:
                if column not in old_schema:
                    if "DEFAULT" not in column:
                        log.error(f"Cannot add column {column.split()[0]} to {table_name}: a default must be applied when adding a NOT NULL field to the database.")
                        return
                    query_string = f"ALTER TABLE {table_name} ADD COLUMN {column}"
                    column_additions.append(query_string)
                    
            for column in old_schema:
                if column not in schema:
                    query_string = f"ALTER TABLE {table_name} DROP COLUMN {column.split()[0]}"
                    column_additions.append(query_string)
            
            log.log("Creating SQL query...")
            schema_text = ", ".join(schema)
            column_names_text = ", ".join(cls.get_columns())
            table_columns_addition = f"; ".join(column_additions)
            table_creation = f"CREATE TABLE IF NOT EXISTS {table_name}_tmp({schema_text})"
            table_movement = f"INSERT INTO {table_name}_tmp ({column_names_text}) SELECT {column_names_text} FROM {table_name}"
            table_deletion = f"DROP TABLE {table_name}"
            table_rename = f"ALTER TABLE {table_name}_tmp RENAME TO {table_name}"
            
            sql_instruction = f"{table_columns_addition};{table_creation};{table_movement};{table_deletion};{table_rename};"
        
        migration_data = {
            "sql": sql_instruction,
            "name": migration_name,
            "schema": schema
        }
        
        log.log("Saving migration...")
        with open(f"{self.migrations_path}/{migration_name}.json", "w") as file:
            json.dump(migration_data, file, indent=4)
        db.execute("INSERT INTO migrations (id, model, name, applied) VALUES (?, ?, ?, ?)", (migration_id, table_name, migration_name, False, ))
        db.commit()
        
        log.success(f"Created migration [{migration_name}]")
    
    def makemigrations(self):
        os.makedirs(self.migrations_path, exist_ok=True)
        self.ensure_migrations_table()
        models = self.scan()
        for model in models:
            log.info(f"Making migrations for [{model.__name__.lower()}]")
            self.make_class_migrations(model)
    
    def applymigrations(self):
        log.info("Applying migrations")
        log.log("Fetching unapplied migrations...")
        unapplied_migrations = db.execute("SELECT name FROM migrations WHERE applied=FALSE").fetchall()
        if len(unapplied_migrations) == 0:
            log.error("No unapplied migrations.")
            return

        log.info(f"{len(unapplied_migrations)} unapplied migrations.")
        
        for migration in sorted(unapplied_migrations):
            migration_name = migration[0]
            migration_file = f"{self.migrations_path}/{migration_name}.json"
            log.info(f"Applying migration {migration_name}")
            log.log("Fetching SQL query...")
            with open(migration_file, "r") as file:
                data = json.load(file)
            
            sql = data["sql"]
            log.log("Executing SQL query...")
            db.executescript(sql)
            log.log("Updating migration records...")
            db.execute("UPDATE migrations SET applied=TRUE WHERE name=?", (migration_name, ))
            log.log("Commiting changes...")
            db.commit()
            log.success(f"Succesfully migrated {migration_name}")
            
    
if __name__ == "__main__":
    m = MigrationManager("model.py", "migrations")
    m.makemigrations()
    m.applymigrations()