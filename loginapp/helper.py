"""
Helper module.

This module handles helper-specific functionality including the helper dashboard.
"""

from loginapp import app
from loginapp import db
from flask import render_template, session
from loginapp.decorators import helper_required

@app.route('/helper/home')
@helper_required
def helper_home():
    """
    Helper Homepage endpoint.
    
    Displays the helper dashboard with issue statistics.
    
    Returns:
        Rendered helper home template with user data and statistics
    """
    with db.get_cursor() as cursor:
        # Get current user data
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['user_id'],))
        user = cursor.fetchone()

        # Get issue statistics
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM issues
            GROUP BY status
        ''')
        stats = {
            'new': 0,
            'open': 0,
            'stalled': 0,
            'resolved': 0
        }
        for row in cursor.fetchall():
            stats[row['status']] = row['count']

    return render_template('helper_home.html', user=user, stats=stats) 