import os
import sys

# Get the current working directory
current_dir = os.getcwd()

# Construct the full path to settings.py
settings_file = os.path.join(current_dir, "settings.py")

# Check if the settings.py file exists
if os.path.isfile(settings_file):
    # Append the current directory to sys.path
    sys.path.append(current_dir)

    # Import the Settings class from settings module
    import settings
else:
    raise FileNotFoundError(f"Settings file that should be located at {settings_file} does not exist.")

Settings = settings