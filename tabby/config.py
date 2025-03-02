import os, sys
path = os.getcwd() + "/settings.py"
path = sys.path.insert(0, path)
Settings = __import__("settings")