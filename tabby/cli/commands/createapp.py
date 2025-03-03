#!/usr/bin/env python3
import os

settings_file = '''import os

BASE_PATH = os.path.dirname(os.path.realpath(__file__)) + "/"
MODELS_PATH = BASE_PATH + "app/models/user.py"
DATABASE_PATH = BASE_PATH + "database/db.sqlite3"
MIGRATIONS_PATH = BASE_PATH + "database/migrations/"
DATABASE_ADAPTER = "SQLite"'''

structure = {
    "app": {
        "models": {
            "user.py": ""
        },
    },
    "database": {
        "migrations": {},
        "db.sqlite3": "",
    },
    "main.py": "",
    "settings.py": settings_file
}

def gen_file(path, contents):
    print(f"Creating file {path}")
    with open(f"{path}", "w") as file:
        file.write(contents)

def gen_directory(path, contents):
    os.mkdir(path)
    print(f"Generating directory {path}")
    for n, c in contents.items():
        if isinstance(c, dict):
            gen_directory(f"{path}/{n}", c)
        if isinstance(c, str):
            gen_file(f"{path}/{n}", c)

def gen_project(directory, name):
    starting_directory = f"{directory}/{name}"
    os.mkdir(f"{starting_directory}")
    for name, contents in structure.items():
        if isinstance(contents, dict):
            gen_directory(f"{starting_directory}/{name}", contents)
        if isinstance(contents, str):
            gen_file(f"{starting_directory}/{name}", contents)

def ExecuteCommand(args):
    gen_project(os.getcwd(), args[1])