"""
Visitor module.

This module handles visitor-specific functionality including the visitor dashboard.
"""

from loginapp import app
from loginapp import db
from flask import render_template, session, url_for
from loginapp.decorators import login_required

@app.route('/visitor/home')
@login_required
def visitor_home():
    """
    Visitor Homepage endpoint.
    
    Displays the visitor dashboard.
    
    Returns:
        Rendered visitor home template with user data
    """
    # Check if user is a visitor
    if session['role'] != 'visitor':
        return render_template('access_denied.html'), 403
        
    with db.get_cursor() as cursor:
        # Get current user data
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['user_id'],))
        user = cursor.fetchone()
        
    return render_template('visitor_home.html', user=user) 