from __init__ import app, db
from models import User
from werkzeug.security import generate_password_hash
from datetime import datetime

if __name__ == '__main__':
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create admin user if not exists
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
            print("Admin user created successfully!")
    
    app.run(debug=True)
