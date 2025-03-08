"""
Decorators module.

This module provides custom decorators for route access control.
"""

from functools import wraps
from flask import session, redirect, url_for, render_template

def login_required(f):
    """
    Decorator to check if user is logged in.
    
    Args:
        f: The function to be decorated
        
    Returns:
        The decorated function that checks login status before execution
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator to check if user is an admin.
    
    Args:
        f: The function to be decorated
        
    Returns:
        The decorated function that checks admin status before execution
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        if session['role'] != 'admin':
            return render_template('access_denied.html'), 403
        return f(*args, **kwargs)
    return decorated_function

def helper_required(f):
    """
    Decorator to check if user is a helper.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        if session['role'] != 'helper':
            return render_template('access_denied.html'), 403
        return f(*args, **kwargs)
    return decorated_function

def helper_or_admin_required(f):
    """
    Decorator to check if user is a helper or admin.
    
    Args:
        f: The function to be decorated
        
    Returns:
        The decorated function that checks helper/admin status before execution
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        if session['role'] not in ['helper', 'admin']:
            return render_template('access_denied.html'), 403
        return f(*args, **kwargs)
    return decorated_function 