from loginapp import app
from loginapp import db
from flask import redirect, render_template, request, session, url_for, flash
from flask_bcrypt import Bcrypt
import os
from werkzeug.utils import secure_filename
from loginapp.utils import save_profile_image, delete_profile_image
from loginapp.decorators import login_required

# Create an instance of the Bcrypt class, which we'll be using to hash user
# passwords during login and registration.
flask_bcrypt = Bcrypt()

# Default role for new users
DEFAULT_USER_ROLE = 'visitor'

# Password validation pattern
# At least 8 characters, must include uppercase, lowercase, and numbers
PASSWORD_PATTERN = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'

# Add these constants at the top of the file
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join('loginapp', 'static', 'uploads', 'profiles')
DEFAULT_AVATAR = '300.jpeg'

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def user_home_url():
    """Generates a URL to the homepage for the currently logged-in user.
    
    If the user is not logged in, this returns the URL for the login page
    instead. If the user appears to be logged in, but the role stored in their
    session cookie is invalid (i.e. not a recognised role), it returns the URL
    for the logout page to clear that invalid session data."""
    if 'loggedin' in session:
        role = session.get('role', None)
        if role == 'visitor':
            home_endpoint = 'visitor_home'
        elif role == 'helper':
            home_endpoint = 'helper_home'
        elif role == 'admin':
            home_endpoint = 'admin_home'
        else:
            home_endpoint = 'logout'
    else:
        home_endpoint = 'login'
    
    return url_for(home_endpoint)

@app.route('/')
def root():
    """Root endpoint (/)
    
    Methods:
    - get: Redirects guests to the login page, and redirects logged-in users to
        their own role-specific homepage.
    """
    return redirect(user_home_url())

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page endpoint.

    Methods:
    - get: Renders the login page.
    - post: Attempts to log the user in using the credentials supplied via the
        login form, and either:
        - Redirects the user to their role-specific homepage (if successful)
        - Renders the login page again with an error message (if unsuccessful).
    
    If the user is already logged in, both get and post requests will redirect
    to their role-specific homepage.
    """
    if 'loggedin' in session:
        return redirect(user_home_url())

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with db.get_cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            user = cursor.fetchone()

        if user and flask_bcrypt.check_password_hash(user['password_hash'], password):
            if user['status'] != 'active':
                flash('Your account is inactive. Please contact an administrator for assistance.', 'danger')
                return render_template('login.html', username=username, error=True)
                
            session['loggedin'] = True
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['first_name'] = user['first_name']
            session['profile_image'] = user['profile_image']
            
            return redirect(user_home_url())
        else:
            flash('Invalid username or password', 'danger')
            return render_template('login.html', username=username, error=True)

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Sign up page endpoint."""
    if request.method == 'POST':
        # Get form data
        form_data = {
            'username': request.form.get('username', '').strip(),
            'password': request.form.get('password', ''),
            'confirm_password': request.form.get('confirm_password', ''),
            'email': request.form.get('email', '').strip(),
            'first_name': request.form.get('first_name', '').strip(),
            'last_name': request.form.get('last_name', '').strip(),
            'location': request.form.get('location', '').strip()
        }
        
        # Validate input
        errors = {}
        
        # Validate username
        if not re.match(r'^[A-Za-z0-9_-]{3,20}$', form_data['username']):
            errors['username'] = 'Username must be 3-20 characters and contain only letters, numbers, underscores, and hyphens'

        # Validate email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', form_data['email']):
            errors['email'] = 'Please enter a valid email address'

        # Validate password
        if not re.match(PASSWORD_PATTERN, form_data['password']):
            errors['password'] = 'Password must be at least 8 characters and include uppercase, lowercase, and numbers'

        # Validate first_name and last_name
        if not form_data['first_name'].strip():
            errors['first_name'] = 'First name is required'
        if not form_data['last_name'].strip():
            errors['last_name'] = 'Last name is required'

        # Validate location
        if not form_data['location'].strip():
            errors['location'] = 'Location is required'

        # Validate password match
        if form_data['password'] != form_data['confirm_password']:
            errors['confirm_password'] = 'Passwords do not match'

        if not errors:
            try:
                with db.get_cursor() as cursor:
                    # Check if username already exists
                    cursor.execute('SELECT * FROM users WHERE username = %s', 
                                 (form_data['username'],))
                    if cursor.fetchone():
                        errors['username'] = 'Username already exists'
                        return render_template('signup.html', errors=errors, **form_data)

                    # Check if email already exists
                    cursor.execute('SELECT * FROM users WHERE email = %s', 
                                 (form_data['email'],))
                    if cursor.fetchone():
                        errors['email'] = 'Email already registered'
                        return render_template('signup.html', errors=errors, **form_data)

                    # Hash password
                    hashed_password = flask_bcrypt.generate_password_hash(form_data['password'])
                    
                    # Create new user
                    cursor.execute('''
                        INSERT INTO users (username, password_hash, email, first_name, 
                                        last_name, location, role, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (form_data['username'], hashed_password, form_data['email'],
                          form_data['first_name'], form_data['last_name'], 
                          form_data['location'], 'visitor', 'active'))
                    db.get_db().commit()
                    
                    # Store registration data in session for auto-fill login
                    session['registration_data'] = {
                        'username': form_data['username'],
                        'password': form_data['password'],
                        'show_welcome': True
                    }
                    
                    flash('Account created successfully! Please log in with your credentials.', 'success')
                    return redirect(url_for('login'))
            except Exception as e:
                flash('Failed to create account', 'danger')
                return render_template('signup.html', errors=errors, **form_data)
        
        return render_template('signup.html', errors=errors, **form_data)

    # GET request - show empty form
    return render_template('signup.html', errors={})

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User Profile page endpoint."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    # Initialize empty errors dict
    errors = {}

    if request.method == 'POST':
        form_data = {
            'email': request.form['email'],
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'location': request.form['location']
        }

        # Validate form data...
        if not errors:
            try:
                with db.get_cursor() as cursor:
                    # Update user data
                    cursor.execute('''
                        UPDATE users 
                        SET email = %s, first_name = %s, last_name = %s, 
                            location = %s
                        WHERE user_id = %s
                    ''', (form_data['email'], form_data['first_name'], 
                          form_data['last_name'], form_data['location'], 
                          session['user_id']))

                # Handle profile image upload
                if 'profile_image' in request.files and request.files['profile_image'].filename:
                    file = request.files['profile_image']
                    if file and allowed_file(file.filename):
                        # Delete old profile image if exists
                        if session['profile_image']:
                            delete_profile_image(session['profile_image'])
                        
                        # Save new profile image
                        filename = save_profile_image(file, session['username'])
                        
                        # Update database
                        cursor.execute('UPDATE users SET profile_image = %s WHERE user_id = %s',
                                     (filename, session['user_id']))
                        db.get_db().commit()
                        # Update session
                        session['profile_image'] = filename
                    else:
                        errors['profile_image'] = 'Invalid file format'
                
                # Handle profile image removal
                if request.form.get('remove_profile_image') == 'true' and session['profile_image']:
                    # Delete profile image
                    delete_profile_image(session['profile_image'])
                    
                    # Update database
                    cursor.execute('UPDATE users SET profile_image = NULL WHERE user_id = %s',
                                 (session['user_id'],))
                    db.get_db().commit()
                    
                    # Update session
                    session.pop('profile_image', None)

                db.get_db().commit()
                flash('Profile updated successfully', 'success')
                return redirect(url_for('profile'))
            except Exception as e:
                flash('Failed to update profile', 'danger')
                return redirect(url_for('profile'))
        else:
            for field, error in errors.items():
                flash(f'{error}', 'danger')

    # Get current user data
    with db.get_cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE user_id = %s', 
                      (session['user_id'],))
        user = cursor.fetchone()

    # Always pass errors dict to template, even if empty
    return render_template('profile.html', user=user, errors=errors)

@app.route('/logout')
def logout():
    """Logout endpoint.

    Methods:
    - get: Logs the current user out (if they were logged in to begin with),
        and redirects them to the login page.
    """
    # Note that nothing actually happens on the server when a user logs out: we
    # just remove the cookie from their web browser. They could technically log
    # back in by manually restoring the cookie we've just deleted. In a high-
    # security web app, you may need additional protections against this (e.g.
    # keeping a record of active sessions on the server side).
    session.clear()
    
    return redirect(url_for('login'))

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'loggedin' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    with db.get_cursor() as cursor:
        cursor.execute('SELECT password_hash FROM users WHERE user_id = %s', 
                      (session['user_id'],))
        user = cursor.fetchone()

    if not flask_bcrypt.check_password_hash(user['password_hash'], current_password):
        return jsonify({
            'success': False,
            'error': 'Current password is incorrect'
        })

    # Check if new password is same as current password
    if flask_bcrypt.check_password_hash(user['password_hash'], new_password):
        return jsonify({
            'success': False,
            'error': 'New password cannot be the same as current password'
        })

    if not re.match(PASSWORD_PATTERN, new_password):
        return jsonify({
            'success': False,
            'error': 'Password must be at least 8 characters and include uppercase, lowercase, and numbers'
        })

    # Update password
    hashed_password = flask_bcrypt.generate_password_hash(new_password)
    with db.get_cursor() as cursor:
        cursor.execute('UPDATE users SET password_hash = %s WHERE user_id = %s',
                      (hashed_password, session['user_id']))
        db.get_db().commit()
        flash('Password updated successfully', 'success')

    return jsonify({
        'success': True
    })

@app.route('/upload_profile_image', methods=['POST'])
def upload_profile_image():
    """Handle profile image upload."""
    if 'loggedin' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    if 'profile_image' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})
    
    file = request.files['profile_image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})

    if file:
        # Create filename using username
        filename = f"{session['username']}_image{os.path.splitext(file.filename)[1]}"
        filename = secure_filename(filename)
        
        # Ensure upload directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save file
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Update database
        with db.get_cursor() as cursor:
            cursor.execute('UPDATE users SET profile_image = %s WHERE user_id = %s',
                         (filename, session['user_id']))
            db.get_db().commit()
        
        return jsonify({'success': True, 'filename': filename})

    return jsonify({'success': False, 'error': 'File upload failed'})

@app.route('/delete_profile_image', methods=['POST'])
def delete_profile_image():
    """Delete user's profile image."""
    if 'loggedin' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    with db.get_cursor() as cursor:
        # Get current profile image
        cursor.execute('SELECT profile_image FROM users WHERE user_id = %s',
                      (session['user_id'],))
        result = cursor.fetchone()
        
        if result and result['profile_image']:
            # Delete file if it exists
            file_path = os.path.join(UPLOAD_FOLDER, result['profile_image'])
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Update database
            cursor.execute('UPDATE users SET profile_image = NULL WHERE user_id = %s',
                         (session['user_id'],))
            db.get_db().commit()

    return jsonify({'success': True})

@app.route('/update_profile', methods=['POST'])
def update_profile():
    """Update user profile endpoint."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    errors = {}
    form_data = {
        'email': request.form['email'],
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'location': request.form['location']
    }

    # Validate email format
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', form_data['email']):
        errors['email'] = 'Please enter a valid email address'

    # Validate required fields
    if not form_data['first_name'].strip():
        errors['first_name'] = 'First name is required'
    if not form_data['last_name'].strip():
        errors['last_name'] = 'Last name is required'
    if not form_data['location'].strip():
        errors['location'] = 'Location is required'

    # Check if email is already taken by another user
    with db.get_cursor() as cursor:
        cursor.execute('SELECT user_id FROM users WHERE email = %s AND user_id != %s',
                      (form_data['email'], session['user_id']))
        if cursor.fetchone():
            errors['email'] = 'This email is already registered'

    if errors:
        with db.get_cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['user_id'],))
            user = cursor.fetchone()
        return render_template('profile.html', user=user, errors=errors)

    # Update user profile
    with db.get_cursor() as cursor:
        cursor.execute('''
            UPDATE users 
            SET email = %s, first_name = %s, last_name = %s, location = %s 
            WHERE user_id = %s
        ''', (form_data['email'], form_data['first_name'], 
              form_data['last_name'], form_data['location'], 
              session['user_id']))
        db.get_db().commit()

    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))