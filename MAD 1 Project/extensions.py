# extensions.py
# This file contains Flask extensions that will be used across the application
# Separating extensions helps avoid circular import issues

from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy instance without binding it to an app yet
# This will be initialized with the Flask app in app.py
db = SQLAlchemy()
