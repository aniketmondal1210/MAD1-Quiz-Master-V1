# routes.py
# This file contains all the routes (URL endpoints) for the application
# Each route function handles a specific URL and HTTP method

from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Import database and models
from extensions import db
from models import User, Subject, Chapter, Quiz, Question, Score

def register_routes(app):
    """
    Register all routes with the Flask application
    Args:
        app: Flask application instance
    """
    
    # Home page route
    @app.route('/')
    def index():
        """Display the home page"""
        return render_template('index.html')

    # Authentication routes
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Handle user login"""
        if request.method == 'POST':
            # Get form data
            email = request.form.get('email')
            password = request.form.get('password')
            
            # Find user by email
            user = User.query.filter_by(email=email).first()
            
            # Check if user exists and password is correct
            if user and check_password_hash(user.password, password):
                # Store user info in session
                session['user_id'] = user.id
                session['is_admin'] = user.is_admin
                
                # Redirect based on user role
                if user.is_admin:
                    flash('Welcome Admin! You can now create and manage quizzes.', 'success')
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('Welcome! You can now take quizzes.', 'success')
                    return redirect(url_for('user_dashboard'))
            else:
                flash('Invalid email or password', 'danger')
        
        # Display login form for GET requests
        return render_template('login.html')

    # Update the register route in routes.py to handle the modified form
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Handle user registration"""
        if request.method == 'POST':
            # Get form data
            email = request.form.get('email')
            password = request.form.get('password')
            full_name = request.form.get('full_name')
            role = request.form.get('role')
            admin_code = request.form.get('admin_code')
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already registered', 'danger')
                return redirect(url_for('register'))
            
            # Validate admin registration
            is_admin = False
            if role == 'admin':
                if admin_code != 'admin123':  # Simple admin code for demonstration
                    flash('Invalid admin code', 'danger')
                    return redirect(url_for('register'))
                is_admin = True
            
            # Create new user with default values for qualification and dob
            new_user = User(
                email=email,
                password=generate_password_hash(password),
                full_name=full_name,
                qualification="Not specified",  # Default value
                dob=datetime.strptime('2000-01-01', '%Y-%m-%d'),  # Default value
                is_admin=is_admin
            )
            
            # Save user to database
            db.session.add(new_user)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        
        # Display registration form for GET requests
        return render_template('register.html')

    @app.route('/logout')
    def logout():
        """Handle user logout"""
        # Clear user session
        session.pop('user_id', None)
        session.pop('is_admin', None)
        return redirect(url_for('index'))

    # User routes
    @app.route('/user/dashboard')
    def user_dashboard():
        """Display user dashboard with available quizzes"""
        # Check if user is logged in and not an admin
        if 'user_id' not in session or session.get('is_admin'):
            return redirect(url_for('login'))
        
        # Get user information
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        # Get all available quizzes
        quizzes = Quiz.query.all()
        
        # Get user's attempted quizzes
        attempted_quizzes = Score.query.filter_by(user_id=user_id).all()
        attempted_quiz_ids = [score.quiz_id for score in attempted_quizzes]
        
        return render_template('user/dashboard.html', user=user, quizzes=quizzes, 
                            attempted_quiz_ids=attempted_quiz_ids)

    @app.route('/user/quiz/<int:quiz_id>')
    def start_quiz(quiz_id):
        """Display quiz questions for the user to attempt"""
        # Check if user is logged in
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user_id = session['user_id']
        
        # Check if user has already attempted this quiz
        existing_attempt = Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
        if existing_attempt:
            flash('You have already attempted this quiz.', 'warning')
            return redirect(url_for('user_dashboard'))
        
        # Get quiz and its questions
        quiz = Quiz.query.get_or_404(quiz_id)
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        
        # If no questions, redirect with a message
        if not questions:
            flash('This quiz does not have any questions yet.', 'warning')
            return redirect(url_for('user_dashboard'))
        
        return render_template('user/quiz.html', quiz=quiz, questions=questions)

    @app.route('/user/submit_quiz/<int:quiz_id>', methods=['POST'])
    def submit_quiz(quiz_id):
        """Process quiz submission and calculate score"""
        # Check if user is logged in
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user_id = session['user_id']
        
        # Check if user has already attempted this quiz
        existing_attempt = Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
        if existing_attempt:
            flash('You have already attempted this quiz.', 'warning')
            return redirect(url_for('user_dashboard'))
        
        # Get quiz and its questions
        quiz = Quiz.query.get_or_404(quiz_id)
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        
        # If no questions, redirect with a message
        if not questions:
            flash('This quiz does not have any questions.', 'warning')
            return redirect(url_for('user_dashboard'))
        
        # Calculate score
        score = 0
        for question in questions:
            selected_option = request.form.get(f'question_{question.id}')
            if selected_option and int(selected_option) == question.correct_option:
                score += 1
        
        # Save score
        new_score = Score(
            quiz_id=quiz_id,
            user_id=user_id,
            score=score,
            total_questions=len(questions),
            timestamp=datetime.now()
        )
        
        db.session.add(new_score)
        db.session.commit()
        
        flash(f'Quiz submitted! Your score: {score}/{len(questions)}', 'success')
        return redirect(url_for('user_scores'))

    @app.route('/user/scores')
    def user_scores():
        """Display user's quiz scores"""
        # Check if user is logged in and not an admin
        if 'user_id' not in session or session.get('is_admin'):
            return redirect(url_for('login'))
        
        user_id = session['user_id']
        scores = Score.query.filter_by(user_id=user_id).all()
        
        return render_template('user/scores.html', scores=scores)

    @app.route('/user/summary')
    def user_summary():
        """Display summary charts of user's performance"""
        # Check if user is logged in and not an admin
        if 'user_id' not in session or session.get('is_admin'):
            return redirect(url_for('login'))
        
        user_id = session['user_id']
        scores = Score.query.filter_by(user_id=user_id).all()
        
        # Prepare data for subject-wise performance chart
        subject_data = {}
        for score in scores:
            quiz = Quiz.query.get(score.quiz_id)
            chapter = Chapter.query.get(quiz.chapter_id)
            subject = Subject.query.get(chapter.subject_id)
            
            if subject.name not in subject_data:
                subject_data[subject.name] = {'total': 0, 'count': 0}
            
            subject_data[subject.name]['total'] += (score.score / score.total_questions) * 100
            subject_data[subject.name]['count'] += 1
        
        # Calculate averages
        subject_labels = []
        subject_averages = []
        
        for subject_name, data in subject_data.items():
            average = data['total'] / data['count'] if data['count'] > 0 else 0
            subject_labels.append(subject_name)
            subject_averages.append(round(average, 1))
        
        # Prepare data for monthly attempts chart
        month_data = {}
        for score in scores:
            month = score.timestamp.strftime('%b %Y')
            if month not in month_data:
                month_data[month] = 0
            month_data[month] += 1
        
        month_labels = list(month_data.keys())
        month_values = list(month_data.values())
        
        # Pass the data to the template
        return render_template('user/summary.html', 
                            subject_labels=subject_labels,
                            subject_averages=subject_averages,
                            month_labels=month_labels,
                            month_values=month_values)

    # Admin routes
    @app.route('/admin/dashboard')
    def admin_dashboard():
        """Display admin dashboard"""
        # Check if user is logged in and is an admin
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('login'))
        
        subjects = Subject.query.all()
        return render_template('admin/dashboard.html', subjects=subjects)

    @app.route('/admin/create-quiz', methods=['GET', 'POST'])
    def create_quiz():
        """Create a new quiz"""
        # Check if user is logged in and is an admin
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('login'))
        
        subjects = Subject.query.all()
        
        if request.method == 'POST':
            # Get form data
            chapter_id = request.form.get('chapter_id')
            date = request.form.get('date')
            duration = request.form.get('duration')
            remarks = request.form.get('remarks')
            
            # Validate chapter exists
            chapter = Chapter.query.get_or_404(chapter_id)
            
            # Create new quiz
            new_quiz = Quiz(
                chapter_id=chapter_id,
                date=datetime.strptime(date, '%Y-%m-%d'),
                duration=duration,
                remarks=remarks
            )
            db.session.add(new_quiz)
            db.session.commit()
            
            flash('Quiz created successfully! Now add questions to your quiz.', 'success')
            return redirect(url_for('admin_questions', quiz_id=new_quiz.id))
        
        return render_template('admin/create_quiz.html', subjects=subjects)

    @app.route('/admin/all-quizzes')
    def all_quizzes():
        """Display all quizzes"""
        # Check if user is logged in and is an admin
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('login'))
        
        quizzes = Quiz.query.all()
        return render_template('admin/all_quizzes.html', quizzes=quizzes)

    @app.route('/admin/subjects', methods=['GET', 'POST'])
    def admin_subjects():
        """Manage subjects"""
        # Check if user is logged in and is an admin
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            # Get form data
            name = request.form.get('name')
            description = request.form.get('description')
            
            # Create new subject
            new_subject = Subject(name=name, description=description)
            db.session.add(new_subject)
            db.session.commit()
            
            flash('Subject added successfully', 'success')
            return redirect(url_for('admin_subjects'))
        
        subjects = Subject.query.all()
        return render_template('admin/subjects.html', subjects=subjects)

    @app.route('/admin/subject/<int:subject_id>/edit', methods=['GET', 'POST'])
    def edit_subject(subject_id):
        """Edit a subject"""
        # Check if user is logged in and is an admin
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('login'))
        
        subject = Subject.query.get_or_404(subject_id)
        
        if request.method == 'POST':
            # Update subject data
            subject.name = request.form.get('name')
            subject.description = request.form.get('description')
            
            db.session.commit()
            flash('Subject updated successfully', 'success')
            return redirect(url_for('admin_subjects'))
        
        return render_template('admin/edit_subject.html', subject=subject)

    @app.route('/admin/subject/<int:subject_id>/delete')
    def delete_subject(subject_id):
        """Delete a subject and all its related data"""
        # Check if user is logged in and is an admin
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('login'))
        
        subject = Subject.query.get_or_404(subject_id)
        
        # Delete associated chapters, quizzes, questions, and scores
        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        for chapter in chapters:
            quizzes = Quiz.query.filter_by(chapter_id=chapter.id).all()
            for quiz in quizzes:
                Question.query.filter_by(quiz_id=quiz.id).delete()
                Score.query.filter_by(quiz_id=quiz.id).delete()
            Quiz.query.filter_by(chapter_id=chapter.id).delete()
        Chapter.query.filter_by(subject_id=subject_id).delete()
        
        db.session.delete(subject)
        db.session.commit()
        
        flash('Subject deleted successfully', 'success')
        return redirect(url_for('admin_subjects'))

    @app.route('/admin/chapters/<int:subject_id>', methods=['GET', 'POST'])
    def admin_chapters(subject_id):
        """Manage chapters for a subject"""
        # Check if user is logged in and is an admin
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('login'))
        
        subject = Subject.query.get_or_404(subject_id)
        
        if request.method == 'POST':
            # Get form data
            name = request.form.get('name')
            description = request.form.get('description')
            
            # Create new chapter
            new_chapter = Chapter(name=name, description=description, subject_id=subject_id)
            db.session.add(new_chapter)
            db.session.commit()
            
            flash('Chapter added successfully', 'success')
            return redirect(url_for('admin_chapters', subject_id=subject_id))
        
        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        return render_template('admin/chapters.html', subject=subject, chapters=chapters)

    @app.route('/admin/chapter/<int:chapter_id>/edit', methods=['GET', 'POST'])
    def edit_chapter(chapter_id):
        """Edit a chapter"""
        # Check if user is logged in and is an admin
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('login'))
        
        chapter = Chapter.query.get_or_404(chapter_id)
        
        if request.method == 'POST':
            # Update chapter data
            chapter.name = request.form.get('name')
            chapter.description = request.form.get('description')
            
            db.session.commit()
            flash('Chapter updated successfully', 'success')
            return redirect(url_for('admin_chapters', subject_id=chapter.subject_id))
        
        return render_template('admin/edit_chapter.html', chapter=chapter)

    @app.route('/admin/chapter/<int:chapter_id>/delete')
    def delete_chapter(chapter_id):
        """Delete a chapter and all its related data"""
        # Check if user is logged in and is an admin
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('login'))
        
        chapter = Chapter.query.get_or_404(chapter_id)
        subject_id = chapter.subject_id
        
        # Delete associated quizzes, questions, and scores
        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
        for quiz in quizzes:
            Question.query.filter_by(quiz_id=quiz.id).delete()
            Score.query.filter_by(quiz_id=quiz.id).delete()
        Quiz.query.filter_by(chapter_id=chapter_id).delete()
        
        db.session.delete(chapter)
        db.session.commit()
        
        flash('Chapter deleted successfully', 'success')
        return redirect(url_for('admin_chapters', subject_id=subject_id))

    @app.route('/admin/quizzes/<int:chapter_id>', methods=['GET', 'POST'])
    def admin_quizzes(chapter_id):
        """Manage quizzes for a chapter"""
        # Check if user is logged in and is an admin
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('login'))
        
        chapter = Chapter.query.get_or_404(chapter_id)
        
        if request.method == 'POST':
            # Get form data
            date = request.form.get('date')
            duration = request.form.get('duration')
            remarks = request.form.get('remarks')
            
            # Create new quiz
            new_quiz = Quiz(
                chapter_id=chapter_id,
                date=datetime.strptime(date, '%Y-%m-%d'),
                duration=duration,
                remarks=remarks
            )
            db.session.add(new_quiz)
            db.session.commit()
            
            flash('Quiz added successfully', 'success')
            return redirect(url_for('admin_quizzes', chapter_id=chapter_id))
        
        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
        return render_template('admin/quizzes.html', chapter=chapter, quizzes=quizzes)

    @app.route('/admin/quiz/<int:quiz_id>/edit', methods=['GET', 'POST'])
    def edit_quiz(quiz_id):
        """Edit a quiz"""
        # Check if user is logged in and is an admin
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('login'))
        
        quiz = Quiz.query.get_or_404(quiz_id)
        
        if request.method == 'POST':
            # Update quiz data
            quiz.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
            quiz.duration = request.form.get('duration')
            quiz.remarks = request.form.get('remarks')
            
            db.session.commit()
            flash('Quiz updated successfully', 'success')
            return redirect(url_for('admin_quizzes', chapter_id=quiz.chapter_id))
        
        return render_template('admin/edit_quiz.html', quiz=quiz)

    @app.route('/admin/quiz/<int:quiz_id>/delete')
    def delete_quiz(quiz_id):
        """Delete a quiz and all its related data"""
        # Check if user is logged in and is an admin
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('login'))
        
        quiz = Quiz.query.get_or_404(quiz_id)
        chapter_id = quiz.chapter_id
        
        # Delete associated questions and scores
        Question.query.filter_by(quiz_id=quiz_id).delete()
        Score.query.filter_by(quiz_id=quiz_id).delete()
        
        db.session.delete(quiz)
        db.session.commit()
        
        flash('Quiz deleted successfully', 'success')
        return redirect(url_for('admin_quizzes', chapter_id=chapter_id))

    @app.route('/admin/questions/<int:quiz_id>', methods=['GET', 'POST'])
    def admin_questions(quiz_id):
        """Manage questions for a quiz"""
        # Check if user is logged in and is an admin
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('login'))
        
        quiz = Quiz.query.get_or_404(quiz_id)
        
        if request.method == 'POST':
            # Get form data
            question_text = request.form.get('question_text')
            option1 = request.form.get('option1')
            option2 = request.form.get('option2')
            option3 = request.form.get('option3')
            option4 = request.form.get('option4')
            correct_option = int(request.form.get('correct_option'))
            
            # Create new question
            new_question = Question(
                quiz_id=quiz_id,
                question_text=question_text,
                option1=option1,
                option2=option2,
                option3=option3,
                option4=option4,
                correct_option=correct_option
            )
            db.session.add(new_question)
            db.session.commit()
            
            flash('Question added successfully', 'success')
            return redirect(url_for('admin_questions', quiz_id=quiz_id))
        
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        return render_template('admin/questions.html', quiz=quiz, questions=questions)

    @app.route('/admin/question/<int:question_id>/edit', methods=['GET', 'POST'])
    def edit_question(question_id):
        """Edit a question"""
        # Check if user is logged in and is an admin
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('login'))
        
        question = Question.query.get_or_404(question_id)
        
        if request.method == 'POST':
            # Update question data
            question.question_text = request.form.get('question_text')
            question.option1 = request.form.get('option1')
            question.option2 = request.form.get('option2')
            question.option3 = request.form.get('option3')
            question.option4 = request.form.get('option4')
            question.correct_option = int(request.form.get('correct_option'))
            
            db.session.commit()
            flash('Question updated successfully', 'success')
            return redirect(url_for('admin_questions', quiz_id=question.quiz_id))
        
        return render_template('admin/edit_question.html', question=question)

    @app.route('/admin/question/<int:question_id>/delete')
    def delete_question(question_id):
        """Delete a question"""
        # Check if user is logged in and is an admin
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('login'))
        
        question = Question.query.get_or_404(question_id)
        quiz_id = question.quiz_id
        
        db.session.delete(question)
        db.session.commit()
        
        flash('Question deleted successfully', 'success')
        return redirect(url_for('admin_questions', quiz_id=quiz_id))

    @app.route('/admin/summary')
    def admin_summary():
        """Display summary charts for the admin"""
        # Check if user is logged in and is an admin
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('login'))
        
        # Get all subjects and their scores
        subjects = Subject.query.all()
        subject_data = {}
        
        for subject in subjects:
            subject_data[subject.name] = {
                'top_score': 0,
                'attempts': 0
            }
            
            for chapter in subject.chapters:
                for quiz in chapter.quizzes:
                    scores = Score.query.filter_by(quiz_id=quiz.id).all()
                    subject_data[subject.name]['attempts'] += len(scores)
                    
                    for score in scores:
                        percentage = (score.score / score.total_questions) * 100
                        if percentage > subject_data[subject.name]['top_score']:
                            subject_data[subject.name]['top_score'] = percentage
        
        return render_template('admin/summary.html', subject_data=subject_data)

    # API route to get chapters for a subject
    @app.route('/api/chapters/<int:subject_id>')
    def get_chapters(subject_id):
        """API endpoint to get chapters for a subject"""
        # Check if user is logged in and is an admin
        if 'user_id' not in session or not session.get('is_admin'):
            return jsonify([])
        
        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        chapters_data = [{'id': chapter.id, 'name': chapter.name} for chapter in chapters]
        
        return jsonify(chapters_data)
