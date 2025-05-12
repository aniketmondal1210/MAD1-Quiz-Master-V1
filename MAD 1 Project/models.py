# models.py
# This file defines all the database models (tables) for the application
# Each class represents a table in the database

from datetime import datetime
from extensions import db

class User(db.Model):
    """
    User model - Stores information about both regular users and administrators
    """
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each user
    email = db.Column(db.String(100), unique=True, nullable=False)  # Email (used as username)
    password = db.Column(db.String(200), nullable=False)  # Hashed password
    full_name = db.Column(db.String(100), nullable=False)  # User's full name
    qualification = db.Column(db.String(100), nullable=False)  # User's qualification
    dob = db.Column(db.DateTime, nullable=False)  # Date of birth
    is_admin = db.Column(db.Boolean, default=False)  # True for admin, False for regular user
    scores = db.relationship('Score', backref='user', lazy=True)  # Link to user's quiz scores
    
    def __repr__(self):
        return f'<User {self.email}>'

class Subject(db.Model):
    """
    Subject model - Represents a field of study (e.g., Mathematics, Science)
    """
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each subject
    name = db.Column(db.String(100), nullable=False)  # Subject name
    description = db.Column(db.Text, nullable=True)  # Subject description
    # Link to chapters in this subject (cascade ensures chapters are deleted when subject is deleted)
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Subject {self.name}>'

class Chapter(db.Model):
    """
    Chapter model - Represents a module within a subject (e.g., Algebra in Mathematics)
    """
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each chapter
    name = db.Column(db.String(100), nullable=False)  # Chapter name
    description = db.Column(db.Text, nullable=True)  # Chapter description
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)  # Link to parent subject
    # Link to quizzes in this chapter (cascade ensures quizzes are deleted when chapter is deleted)
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Chapter {self.name}>'

class Quiz(db.Model):
    """
    Quiz model - Represents a test for a specific chapter
    """
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each quiz
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)  # Link to parent chapter
    date = db.Column(db.DateTime, nullable=False)  # Date when the quiz is scheduled
    duration = db.Column(db.String(10), nullable=False)  # Duration in HH:MM format
    remarks = db.Column(db.Text, nullable=True)  # Additional notes about the quiz
    # Link to questions in this quiz (cascade ensures questions are deleted when quiz is deleted)
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete-orphan")
    # Link to scores for this quiz (cascade ensures scores are deleted when quiz is deleted)
    scores = db.relationship('Score', backref='quiz', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Quiz {self.id} for Chapter {self.chapter_id}>'

class Question(db.Model):
    """
    Question model - Represents a multiple-choice question in a quiz
    """
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each question
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)  # Link to parent quiz
    question_text = db.Column(db.Text, nullable=False)  # The question itself
    option1 = db.Column(db.String(200), nullable=False)  # First option
    option2 = db.Column(db.String(200), nullable=False)  # Second option
    option3 = db.Column(db.String(200), nullable=False)  # Third option
    option4 = db.Column(db.String(200), nullable=False)  # Fourth option
    correct_option = db.Column(db.Integer, nullable=False)  # Which option is correct (1, 2, 3, or 4)
    
    def __repr__(self):
        return f'<Question {self.id} for Quiz {self.quiz_id}>'

class Score(db.Model):
    """
    Score model - Records a user's performance on a quiz
    """
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each score record
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)  # Link to the quiz
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Link to the user
    score = db.Column(db.Integer, nullable=False)  # Number of correct answers
    total_questions = db.Column(db.Integer, nullable=False)  # Total number of questions
    timestamp = db.Column(db.DateTime, default=datetime.now, nullable=False)  # When the quiz was taken
    
    def __repr__(self):
        return f'<Score {self.score}/{self.total_questions} for User {self.user_id} on Quiz {self.quiz_id}>'
