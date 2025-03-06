"""
Admin module.

This module handles all admin-specific functionality including the admin
dashboard, user management, and user profile viewing.
"""

from loginapp import app
from loginapp import db
from flask import redirect, render_template, session, url_for, request, flash
from loginapp.decorators import admin_required

@app.route('/admin/home')
@admin_required
def admin_home():
    """
    Admin Homepage endpoint.
    
    Displays the admin dashboard with system statistics.
    
    Returns:
        Rendered admin home template with user data and statistics
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
        issue_stats = {
            'new': 0,
            'open': 0,
            'stalled': 0,
            'resolved': 0
        }
        for row in cursor.fetchall():
            issue_stats[row['status']] = row['count']

        # Get user statistics
        cursor.execute('''
            SELECT role, COUNT(*) as count
            FROM users
            WHERE status = 'active'
            GROUP BY role
        ''')
        user_stats = {
            'visitor': 0,
            'helper': 0,
            'admin': 0
        }
        for row in cursor.fetchall():
            user_stats[row['role']] = row['count']

    stats = {
        'issues': issue_stats,
        'users': user_stats
    }

    return render_template('admin_home.html', user=user, stats=stats)

@app.route('/admin/users')
@admin_required
def manage_users():
    """
    User management endpoint.
    
    Displays a list of all users with search functionality.
    
    Returns:
        Rendered user management template with user list
    """
    search = request.args.get('search', '').strip()
    
    with db.get_cursor() as cursor:
        if search:
            cursor.execute('''
                SELECT * FROM users 
                WHERE username LIKE %s 
                   OR first_name LIKE %s 
                   OR last_name LIKE %s
                ORDER BY role, username
            ''', (f'%{search}%', f'%{search}%', f'%{search}%'))
        else:
            cursor.execute('SELECT * FROM users ORDER BY role, username')
        users = cursor.fetchall()

    return render_template('admin/manage_users.html', users=users, active_page='manage_users')

@app.route('/admin/users/<int:user_id>/role', methods=['POST'])
@admin_required
def update_user_role(user_id):
    """
    Update user role endpoint.
    
    Changes a user's role (admin/helper/visitor).
    
    Args:
        user_id: The ID of the user to update
        
    Returns:
        Redirect to user management page
    """
    if user_id == session['user_id']:
        flash('Cannot change your own role', 'error')
        return redirect(url_for('manage_users'))

    new_role = request.form.get('role')
    if new_role not in ['visitor', 'helper', 'admin']:
        flash('Invalid role', 'error')
        return redirect(url_for('manage_users'))

    with db.get_cursor() as cursor:
        cursor.execute('UPDATE users SET role = %s WHERE user_id = %s', 
                      (new_role, user_id))
        db.get_db().commit()
        flash('User role updated successfully', 'success')

    return redirect(url_for('manage_users'))

@app.route('/admin/users/<int:user_id>/status', methods=['POST'])
@admin_required
def update_user_status(user_id):
    """
    Update user status endpoint.
    
    Changes a user's status (active/inactive).
    
    Args:
        user_id: The ID of the user to update
        
    Returns:
        Redirect to user management page
    """
    if user_id == session['user_id']:
        flash('Cannot change your own status', 'error')
        return redirect(url_for('manage_users'))

    new_status = request.form.get('status')
    if new_status not in ['active', 'inactive']:
        flash('Invalid status', 'error')
        return redirect(url_for('manage_users'))

    with db.get_cursor() as cursor:
        cursor.execute('UPDATE users SET status = %s WHERE user_id = %s',
                      (new_status, user_id))
        db.get_db().commit()
        flash('User status updated successfully', 'success')

    return redirect(url_for('manage_users'))

@app.route('/admin/users/<int:user_id>')
@admin_required
def view_user(user_id):
    """
    View user profile endpoint.
    
    Displays a user's profile information.
    
    Args:
        user_id: The ID of the user to view
        
    Returns:
        Rendered profile template with user data
        Redirect to profile page if viewing own profile
        Redirect to user management if user not found
    """
    # If viewing own profile, redirect to profile page
    if user_id == session['user_id']:
        return redirect(url_for('profile'))

    with db.get_cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('manage_users'))

    return render_template('profile.html', user=user, is_admin_view=True)