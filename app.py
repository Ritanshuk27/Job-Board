# job-board/app.py
from flask import Flask, render_template, request, redirect, url_for, g, flash, session
import sqlite3
import os
from datetime import datetime
# Import security utilities for password hashing
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps # For creating the login_required decorator

app = Flask(__name__)
# IMPORTANT: This secret key is CRITICAL for session security.
# Replace with a long, random string in production!
app.secret_key = 'your_very_secure_and_long_secret_key_for_sessions_123!@#ABC'

# Define the path for the SQLite database file
DATABASE = 'database.db'

# --- Database Helper Functions ---

def get_db():
    """
    Establishes a database connection or returns the existing one.
    This function ensures that a single database connection is used per request.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES # This helps in converting TIMESTAMP to Python datetime objects
        )
        g.db.row_factory = sqlite3.Row # Allows accessing columns by name (e.g., row['column_name'])
    return g.db

def close_db(e=None):
    """
    Closes the database connection at the end of the request.
    This function is registered to be called automatically by Flask.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """
    Initializes the database schema and creates tables if they don't exist.
    It reads SQL commands from `schema.sql` to set up the tables.
    """
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit() # Commit the changes to create the tables
    print("Database initialized successfully.")

# Register the close_db function to be called after each request
app.teardown_appcontext(close_db)

# --- Authentication and User Management ---

def get_user(user_id):
    """Fetches a user from the database by ID."""
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    return user

@app.before_request
def load_logged_in_user():
    """Loads the logged-in user from the session before each request."""
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_user(user_id)

def login_required(view):
    """
    A decorator to ensure a user is logged in to access certain views.
    If not logged in, it redirects them to the login page.
    """
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

# --- Jinja2 Context Processor ---
# This makes `now` and `g.user` available in all templates
@app.context_processor
def inject_globals():
    return {'now': datetime.utcnow(), 'user': g.user}

# --- Flask Routes ---

@app.route('/')
def index():
    """
    Home Page: Displays a list of all job postings.
    Jobs are ordered by date_posted in descending order (most recent first).
    """
    db = get_db()
    # Fetch all jobs from the 'jobs' table
    jobs = db.execute('SELECT * FROM jobs ORDER BY date_posted DESC').fetchall()
    return render_template('index.html', jobs=jobs)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    """
    Job Details Page: Displays full details of a specific job.
    Fetches job by its ID. If not found, flashes an error and redirects to home.
    """
    db = get_db()
    job = db.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
    if job is None:
        flash('Sorry, the job you are looking for was not found.', 'error')
        return redirect(url_for('index'))
    return render_template('job_detail.html', job=job)

@app.route('/post-job', methods=('GET', 'POST'))
@login_required # Only logged-in users can post jobs
def post_job():
    """
    Post New Job Page: Allows an administrator (any logged-in user for now) to add new job postings.
    Handles both displaying the form (GET) and processing form submission (POST).
    """
    if request.method == 'POST':
        title = request.form['title']
        company = request.form['company']
        location = request.form['location']
        salary = request.form['salary']
        description = request.form['description']
        job_type = request.form.get('type', 'Full-time')

        # Basic server-side validation
        if not all([title, company, location, description]):
            flash('All required fields (Job Title, Company, Location, Description) must be filled!', 'error')
        else:
            db = get_db()
            db.execute(
                'INSERT INTO jobs (title, company, location, salary, description, type) VALUES (?, ?, ?, ?, ?, ?)',
                (title, company, location, salary, description, job_type)
            )
            db.commit() # Save the new job to the database
            flash('Job posted successfully! It is now visible on the Job Board.', 'success')
            return redirect(url_for('index')) # Redirect to home page after successful post
    return render_template('post_job.html')

@app.route('/apply/<int:job_id>', methods=('GET', 'POST'))
def apply_to_job(job_id):
    """
    Apply to Job Page: Form for applicants to submit their details for a specific job.
    Handles displaying the application form (GET) and processing application submission (POST).
    """
    db = get_db()
    job = db.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()

    if job is None:
        flash('Sorry, the job you are trying to apply for does not exist.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        applicant_name = request.form['applicant_name']
        email = request.form['email']
        message = request.form['message']
        resume_path = 'resume_uploaded_placeholder.pdf' # Storing a dummy string

        # Basic server-side validation
        if not all([applicant_name, email]):
            flash('Your Name and Email Address are required to submit an application.', 'error')
        else:
            db.execute(
                'INSERT INTO applications (job_id, applicant_name, email, resume_path, message) VALUES (?, ?, ?, ?, ?)',
                (job_id, applicant_name, email, resume_path, message)
            )
            db.commit() # Save the application to the database
            flash(f'Thank you, {applicant_name}! Your application for "{job.title}" has been submitted successfully.', 'success')
            return redirect(url_for('job_detail', job_id=job_id)) # Redirect back to job details
    return render_template('apply.html', job=job)

@app.route('/admin/applications')
@login_required # Only logged-in users can view applications
def admin_applications():
    """
    Admin Applications Page: Allows viewing of all submitted job applications.
    Fetches applications along with relevant job details by joining tables.
    """
    db = get_db()
    applications = db.execute('''
        SELECT
            a.id AS application_id,
            a.applicant_name,
            a.email,
            a.message,
            a.application_date,
            j.title AS job_title,
            j.company,
            j.id AS job_id
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        ORDER BY a.application_date DESC
    ''').fetchall() # Fetch all matching records
    return render_template('admin_applications.html', applications=applications)

@app.route('/signup', methods=('GET', 'POST'))
def signup():
    """
    User Signup Page: Allows new users to register an account.
    Hashes password before storing.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        elif db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone() is not None:
            error = f"User '{username}' is already registered."

        if error is None:
            # Hash the password before storing it for security
            hashed_password = generate_password_hash(password)
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            db.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        flash(error, 'error')
    return render_template('signup.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    """
    User Login Page: Allows registered users to log in.
    Verifies password and sets user ID in session on success.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # Store user ID in session
            session.clear()
            session['user_id'] = user['id']
            flash(f'Welcome back, {user["username"]}! You have been logged in.', 'success')
            return redirect(url_for('index')) # Redirect to home page after login
        flash(error, 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logs out the current user by clearing the session."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# --- CLI Command for Database Initialization ---

@app.cli.command('initdb')
def initdb_command():
    """
    Flask CLI command to initialize the database.
    Run this from your terminal: `flask --app app initdb`
    This will delete existing data and create new tables, adding dummy jobs.
    """
    init_db()
    print('Database initialized: Tables created and dummy jobs inserted.')

# --- Main entry point for running the Flask app ---
if __name__ == '__main__':
    # This block is executed when you run 'python app.py' directly.
    # It checks if the database file exists; if not, it initializes it.
    if not os.path.exists(DATABASE):
        with app.app_context(): # Ensure we are in an application context for database operations
            init_db()
    app.run(debug=True) # Run Flask in debug mode. Set debug=False for production.