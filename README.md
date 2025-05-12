# Quiz Master

A comprehensive quiz management system built with Flask and SQLite that allows administrators to create and manage quizzes, while users can take quizzes and track their performance.

## Features

### For Administrators
- Create and manage subjects, chapters, and quizzes
- Add multiple-choice questions to quizzes
- View analytics on quiz performance
- Track user attempts and scores
- Secure admin authentication

### For Users
- Take quizzes on various subjects
- View scores and performance history
- Track progress with visual charts
- See subject-wise performance analytics

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup Instructions

1. Clone the repository:

```sh
git clone https://github.com/yourusername/quiz-master.git
cd quiz-master
```

2. Create a virtual environment:

```sh
python -m venv venv
```

3. Activate the virtual environment:
- On Windows:

```sh
venv\Scripts\activate
```

- On macOS/Linux:

```sh
source venv/bin/activate
```

4. Install the required packages:

```sh
pip install flask flask-sqlalchemy werkzeug
```

5. Initialize the database:

```sh
python run.py
```

This will create the database and add an admin user with the following credentials:
- Email: admin@quizmaster.com
- Password: admin123

## Usage

1. Start the application:

```sh
python run.py
```

2. Open your web browser and navigate to:

```sh
http://127.0.0.1:5000/
```

3. Login with the default admin credentials or register a new user account.

### Admin Workflow
1. Create subjects (e.g., Mathematics, Science)
2. Add chapters to subjects (e.g., Algebra, Geometry)
3. Create quizzes for chapters
4. Add multiple-choice questions to quizzes
5. View analytics and user performance

### User Workflow
1. Browse available quizzes
2. Take quizzes
3. View scores and performance history
4. Track progress with visual charts

## Project Structure

```sh
quiz_master/
├── app.py                  # Main application file
├── routes.py               # URL routes and handlers
├── models.py               # Database models
├── extensions.py           # Flask extensions
├── run.py                  # Application entry point
├── commands.py             # CLI commands
├── reset_db.py             # Database reset utility
├── static/                 # Static files
│   ├── css/
│   │   └── style.css       # Custom CSS styles
│   ├── js/
│   │   └── script.js       # JavaScript functionality
│   └── images/             # Image assets
└── templates/              # HTML templates
    ├── base.html           # Base template
    ├── index.html          # Home page
    ├── login.html          # Login page
    ├── register.html       # Registration page
    ├── admin/              # Admin templates
    │   ├── dashboard.html
    │   ├── subjects.html
    │   ├── chapters.html
    │   ├── quizzes.html
    │   ├── questions.html
    │   └── summary.html
    └── user/               # User templates
        ├── dashboard.html
        ├── quiz.html
        ├── scores.html
        └── summary.html
```

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript
- **CSS Framework**: Bootstrap 5
- **Icons**: Bootstrap Icons
- **Charts**: Chart.js
- **Authentication**: Flask session management with password hashing

## Security Features

- Password hashing using Werkzeug's security functions
- Session-based authentication
- Role-based access control (admin vs. user)
- Form validation
- CSRF protection via Flask's built-in features

## Default Credentials

### Admin User
- Email: admin@quizmaster.com
- Password: admin123

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Flask documentation
- Bootstrap documentation
- Chart.js documentation
- SQLAlchemy documentation
