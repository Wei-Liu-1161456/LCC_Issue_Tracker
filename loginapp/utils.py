"""
Utility functions module.

This module provides utility functions used throughout the application.
"""

import os
from werkzeug.utils import secure_filename
from loginapp import app
from flask import session, url_for

@app.template_global()
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

def save_profile_image(file, username):
    """
    Save a profile image to the uploads directory.
    
    Args:
        file: The uploaded file object
        username: The username to use in the filename
        
    Returns:
        str: The filename of the saved image
    """
    # Define upload folder for profile images
    UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads/profiles')
    
    # Create filename
    filename = f"{username}_image{os.path.splitext(file.filename)[1]}"
    filename = secure_filename(filename)
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Save file
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    
    return filename

def delete_profile_image(filename):
    """
    Delete a profile image from the uploads directory.
    
    Args:
        filename: The filename of the image to delete
        
    Returns:
        bool: True if the file was deleted, False otherwise
    """
    if not filename:
        return False
    
    # Define upload folder for profile images
    UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads/profiles')
    
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

def allowed_file(filename):
    """
    Check if a file has an allowed extension for profile images.
    
    Args:
        filename: The filename to check
        
    Returns:
        bool: True if the file extension is allowed, False otherwise
    """
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS 