#!/usr/bin/env python3
"""
Simple startup script for Quiz Master application
"""

from __init__ import app, create_app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash
from datetime import datetime

def initialize_database():
    """Initialize the database with tables and default admin user"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default admin user if it doesn't exist
        admin = User.query.filter_by(email='admin@quizmaster.com').first()
        if not admin:
            admin = User(
                email='admin@quizmaster.com',
                password=generate_password_hash('admin123'),
                full_name='Admin User',
                qualification='Administrator',
                dob=datetime.strptime('2000-01-01', '%Y-%m-%d'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✓ Default admin user created successfully!")
            print("  Email: admin@quizmaster.com")
            print("  Password: admin123")
        else:
            print("✓ Admin user already exists")

if __name__ == '__main__':
    print("🚀 Starting Quiz Master Application...")
    print("📊 Initializing database...")
    
    try:
        initialize_database()
        print("✅ Database initialized successfully!")
        print("🌐 Starting web server...")
        print("📱 Access the application at: http://127.0.0.1:5000")
        print("🔧 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        app.run(debug=True, host='127.0.0.1', port=5000)
        
    except Exception as e:
        print(f"❌ Error starting application: {str(e)}")
        print("💡 Try running: python reset_db.py first")
