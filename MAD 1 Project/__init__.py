# __init__.py
# Initialize the Flask application

from flask import Flask

def create_app():
    """
    Create and configure the Flask application using the application factory pattern.
    
    Returns: 
        A configured Flask app ready to use
    """
    # Initialize the Flask application
    app = Flask(__name__)
    
    # Configure application settings
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the database with the app
    from extensions import db
    db.init_app(app)
    
    # Import and register routes within app context
    from routes import register_routes
    register_routes(app)
    
    return app

# Create the app instance
app = create_app()
