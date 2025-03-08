"""
User module.

This module handles user authentication, registration, and profile management.
"""

from loginapp import app, db, utils
from flask import redirect, render_template, request, session, url_for, flash, jsonify
from flask_bcrypt import Bcrypt
import re
import os
from werkzeug.utils import secure_filename
from loginapp.decorators import login_required

# Create an instance of the Bcrypt class, which we'll be using to hash user
# passwords during login and registration.
flask_bcrypt = Bcrypt(app)

# Default role for new users
DEFAULT_USER_ROLE = 'visitor'

# Password validation pattern
# At least 8 characters, must include uppercase, lowercase, and numbers
PASSWORD_PATTERN = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'


@app.route('/')
def root():
    """Root endpoint (/)
    
    Methods:
    - get: Redirects guests to the login page, and redirects logged-in users to
        their own role-specific homepage.
    """
    return redirect(utils.user_home_url())

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
        return redirect(utils.user_home_url())

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
            
            return redirect(utils.user_home_url())
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
    """
    User Profile page endpoint.
    
    Allows users to view and update their profile information.
    
    Returns:
        On GET: Rendered profile template with user data
        On POST success: Redirect to profile page with success message
        On POST error: Rendered profile template with validation errors
    """
    # Get current user data
    with db.get_cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['user_id'],))
        user = cursor.fetchone()
    
    # Handle form submission
    if request.method == 'POST':
        # Get form data
        form_data = {
            'first_name': request.form.get('first_name', '').strip(),
            'last_name': request.form.get('last_name', '').strip(),
            'email': request.form.get('email', '').strip(),
            'current_password': request.form.get('current_password', ''),
            'new_password': request.form.get('new_password', ''),
            'confirm_password': request.form.get('confirm_password', '')
        }
        
        # Validate input
        errors = {}
        if not form_data['first_name']:
            errors['first_name'] = 'First name is required'
        if not form_data['last_name']:
            errors['last_name'] = 'Last name is required'
        if not form_data['email']:
            errors['email'] = 'Email is required'
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', form_data['email']):
            errors['email'] = 'Invalid email format'
            
        # Check if email is already in use by another user
        if form_data['email'] != user['email']:
            with db.get_cursor() as cursor:
                cursor.execute('SELECT * FROM users WHERE email = %s AND user_id != %s', 
                             (form_data['email'], session['user_id']))
                if cursor.fetchone():
                    errors['email'] = 'Email is already in use'
        
        # Validate password change if requested
        if form_data['new_password']:
            if not form_data['current_password']:
                errors['current_password'] = 'Current password is required to set a new password'
            elif not flask_bcrypt.check_password_hash(user['password'], form_data['current_password']):
                errors['current_password'] = 'Current password is incorrect'
            
            if len(form_data['new_password']) < 8:
                errors['new_password'] = 'Password must be at least 8 characters long'
            elif not re.search(r'[A-Z]', form_data['new_password']):
                errors['new_password'] = 'Password must contain at least one uppercase letter'
            elif not re.search(r'[a-z]', form_data['new_password']):
                errors['new_password'] = 'Password must contain at least one lowercase letter'
            elif not re.search(r'[0-9!@#$%^&*(),.?":{}|<>]', form_data['new_password']):
                errors['new_password'] = 'Password must contain at least one number or special character'
            
            if form_data['new_password'] != form_data['confirm_password']:
                errors['confirm_password'] = 'Passwords do not match'
        
        if not errors:
            with db.get_cursor() as cursor:
                # Update basic info
                cursor.execute('''
                    UPDATE users 
                    SET first_name = %s, last_name = %s, email = %s
                    WHERE user_id = %s
                ''', (form_data['first_name'], form_data['last_name'], 
                      form_data['email'], session['user_id']))
                
                # Update password if provided
                if form_data['new_password']:
                    hashed_password = flask_bcrypt.generate_password_hash(form_data['new_password']).decode('utf-8')
                    cursor.execute('''
                        UPDATE users 
                        SET password = %s 
                        WHERE user_id = %s
                    ''', (hashed_password, session['user_id']))
                
                # Handle profile image upload
                if 'profile_image' in request.files and request.files['profile_image'].filename:
                    file = request.files['profile_image']
                    if file and utils.allowed_file(file.filename):
                        # Delete old profile image if exists
                        if user['profile_image']:
                            utils.delete_profile_image(user['profile_image'])
                        
                        # Save new profile image
                        filename = utils.save_profile_image(file, session['username'])
                        
                        # Update database
                        cursor.execute('''
                            UPDATE users 
                            SET profile_image = %s 
                            WHERE user_id = %s
                        ''', (filename, session['user_id']))
                        
                        # Update session
                        session['profile_image'] = filename
                    else:
                        errors['profile_image'] = 'Invalid file format'
                
                # Handle profile image removal
                if request.form.get('remove_profile_image') == 'true' and user['profile_image']:
                    # Delete file
                    utils.delete_profile_image(user['profile_image'])
                    
                    # Update database
                    cursor.execute('''
                        UPDATE users 
                        SET profile_image = NULL 
                        WHERE user_id = %s
                    ''', (session['user_id'],))
                    
                    # Update session
                    session['profile_image'] = None
                
                db.get_db().commit()
                
                # Update session data
                session['first_name'] = form_data['first_name']
                session['last_name'] = form_data['last_name']
                
                flash('Profile updated successfully', 'success')
                return redirect(url_for('profile'))
        
        return render_template('profile.html', user=user, errors=errors, form_data=form_data)
    
    # GET request - show profile form
    return render_template('profile.html', user=user, errors={}, form_data={})

@app.route('/logout')
def logout():
    """Logout endpoint.

    Methods:
    - get: Logs the current user out (if they were logged in to begin with),
        and redirects them to the login page.
    """
   
    session.clear()
    
    return redirect(url_for('login'))

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    """
    Change password endpoint.

    Allows users to change their password.

    Methods:
    - post: Allows users to change their password.

    Returns:
    - json: A JSON object containing the success status and error message (if any).
    """
    # if 'loggedin' not in session:
    #     return jsonify({'success': False, 'error': 'Not logged in'}), 401

    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    # Get user data
    with db.get_cursor() as cursor:
        cursor.execute('SELECT password_hash FROM users WHERE user_id = %s', 
                      (session['user_id'],))
        user = cursor.fetchone()

    # Check if current password is correct
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

    # Validate new password
    if not re.match(PASSWORD_PATTERN, new_password):
        return jsonify({
            'success': False,
            'error': 'Password must be 8-20 characters and include uppercase, lowercase, and numbers'
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
