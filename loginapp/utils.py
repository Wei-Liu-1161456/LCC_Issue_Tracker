"""Utility functions for the LCC Issue Tracker application."""

import os
from werkzeug.utils import secure_filename
from loginapp import app, db
from flask import session, url_for
# Add template global function
@app.template_global()
def user_home_url():
    """Return the appropriate home URL based on user role."""
    if 'role' not in session:
        return url_for('login')
    
    role = session['role']
    if role == 'admin':
        return url_for('admin_home')
    elif role == 'helper':
        return url_for('helper_home')
    else:  # visitor
        return url_for('visitor_home')

def save_profile_image(file, username):
    """Save a profile image to the uploads directory.
    
    Args:
        file: The uploaded file object
        username: The username to use in the filename
        
    Returns:
        str: The filename of the saved image
        
    Raises:
        IOError: If the file cannot be saved
    """
    filename = f"{username}_image{os.path.splitext(file.filename)[1]}"
    filename = secure_filename(filename)
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Save file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    return filename

def delete_profile_image(filename):
    """Delete a profile image from the uploads directory.
    
    Args:
        filename: The filename of the image to delete
        
    Returns:
        bool: True if the file was deleted, False otherwise
    """
    if not filename:
        return False
        
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False 