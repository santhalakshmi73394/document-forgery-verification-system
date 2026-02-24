import os

# Absolute path to backend folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Absolute path to project root
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

# Upload and temp folders
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "uploads")
TEMP_FOLDER = os.path.join(PROJECT_ROOT, "temp")

# Create folders if they don’t exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)