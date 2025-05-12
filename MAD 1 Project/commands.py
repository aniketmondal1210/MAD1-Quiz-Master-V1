import click
from flask.cli import with_appcontext
from __init__ import db
from models import User
from werkzeug.security import generate_password_hash
from datetime import datetime

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
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
    
    click.echo('Initialized the database.')

def init_app(app):
    app.cli.add_command(init_db_command)
