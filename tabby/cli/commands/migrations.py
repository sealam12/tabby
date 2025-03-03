#!/usr/bin/env python3
import os
from tabby.database.migrate import MigrationManager
from tabby.utils.config import Settings

def ExecuteCommand(args):
    manager = MigrationManager(Settings.MODELS_PATH, Settings.MIGRATIONS_PATH)
    if args[1] == "make":
        manager.makemigrations()
    if args[1] == "apply":
        manager.applymigrations()