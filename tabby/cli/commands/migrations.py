#!/usr/bin/env python3
import os
from tabby.database.migrate import MigrationManager
from tabby.utils.config import Settings

def ExecuteCommand(args):
    manager = MigrationManager(Settings.MODELS_PATH, Settings.MIGRATIONS_PATH)
    if len(args) < 2:
        print("Usage: tabby migrations [operation]")
        print("Operations")
        print("  make: Creates migrations based off of current models.")
        print("  apply: Applies any created or unapplied migrations to the database.")
        return
    
    if args[1] == "make":
        manager.makemigrations()
    if args[1] == "apply":
        manager.applymigrations()