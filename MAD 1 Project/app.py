# app.py
# This is the main application file that initializes the Flask app
# and sets up the database and routes

from flask import Flask  # Import the Flask class to create our web application
from werkzeug.security import generate_password_hash  # For securely hashing passwords
from datetime import datetime  # For handling dates and times
import os  # For interacting with the operating system

# Import the database object from our extensions file
# This is a SQLAlchemy instance that will be connected to our Flask app
from extensions import db

# Import all our database models (tables)
# These define the structure of our database
from models import User, Subject, Chapter, Quiz, Question, Score

# Create and configure the Flask application
def create_app():
    """
    Create and configure the Flask application using the application factory pattern.
    This pattern allows us to create multiple instances of our app with different configurations.
    
    Returns: 
        A configured Flask app ready to use
    """
    # Initialize the Flask application - this creates the core of our web app
    app = Flask(__name__)
    
    # Configure application settings
    # SECRET_KEY is used for session security (keeping users logged in)
    app.config['SECRET_KEY'] = 'your_secret_key'  
    
    # SQLALCHEMY_DATABASE_URI tells Flask where to find/create the database
    # Here we're using SQLite, which stores the database as a file
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'  
    
    # Disable modification tracking to improve performance
    # This turns off a feature we don't need that would slow down our app
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
    
    # Initialize the database with the app
    # This connects our SQLAlchemy instance to this specific Flask app
    db.init_app(app)
    
    # Import and register routes
    # Routes define what happens when a user visits different URLs in our app
    from routes import register_routes
    register_routes(app)
    
    # Return the fully configured app
    return app

# Initialize database and create admin user
def init_db(app):
    """
    Initialize the database and create the admin user if it doesn't exist.
    This function creates all the necessary tables and ensures there's at least
    one admin user who can manage the system.
    
    Args:
        app: Flask application instance
    """
    # Use the application context to work with the database
    # The app context is needed for database operations
    with app.app_context():
        # Create all database tables based on the models we imported
        # This reads the model definitions and creates corresponding tables
        db.create_all()
        
        # Check if admin user exists by looking for the default admin email
        admin = User.query.filter_by(email='admin@quizmaster.com').first()
        
        # Create admin user if it doesn't exist
        # This ensures there's always an admin who can log in
        if not admin:
            # Create a new User object with admin privileges
            admin = User(
                email='admin@quizmaster.com',  # Default admin email
                # Hash the password for security - never store plain text passwords!
                password=generate_password_hash('admin123'),  
                full_name='Admin User',
                qualification='Administrator',
                # Convert string date to datetime object
                dob=datetime.strptime('2000-01-01', '%Y-%m-%d'),
                is_admin=True  # This flag gives the user admin privileges
            )
            # Add the new admin user to the database session
            db.session.add(admin)
            # Commit the changes to the database
            db.session.commit()
            print("Admin user created successfully!")

# This conditional checks if this file is being run directly (not imported)
if __name__ == '__main__':
    # Create the Flask application using our factory function
    app = create_app()
    
    # Initialize the database and create admin user
    init_db(app)
    
    # Start the development server
    # debug=True enables:
    # - Automatic reloading when code changes
    # - Detailed error pages
    # - Debug console in the browser
    app.run(debug=True)
