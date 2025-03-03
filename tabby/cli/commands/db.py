#!/usr/bin/env python3
import os
from tabby.database.migrate import MigrationManager
from tabby.utils.config import Settings
from tabby.utils import log

def delete_directory():
    log.log("Deleting migrations...")
    migrations = Settings.MIGRATIONS_PATH
    for filename in os.listdir(migrations):
        file_path = os.path.join(migrations, filename)
        
        # Check if it is a file (not a subdirectory)
        if os.path.isfile(file_path):
            os.remove(file_path)  # Remove the file
            log.info(f"Deleted migrations: {filename}")
            
    log.log("Deleting database file...")
    os.remove(Settings.DATABASE_PATH)
    file = open(Settings.DATABASE_PATH, "w")
    file.close()

def ExecuteCommand(args):
    if args[1] == "drop":
        log.warn("Dropping the database will delete all data and all migrations. Continue?")
        if input("Y/n > ") != "Y": return
        log.log("Dropping database")
        delete_directory()
        log.success("Finished database drop")