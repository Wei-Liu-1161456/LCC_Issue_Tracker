# This script runs automatically when our `loginapp` module is first loaded,
# and handles all the setup for our Flask app.
from flask import Flask, url_for, session

app = Flask(__name__)

# Set the "secret key" that our app will use to sign session cookies. This can
# be anything.
# 
# Anyone with access to this key can pretend to be signed in as any user. In a
# real-world project, you wouldn't store this key in your source code. To learn
# about how to manage "secrets" like this in production code, check out
# https://blog.gitguardian.com/how-to-handle-secrets-in-python/
#
# For the purpose of your assignments, you DON'T need to use any of those more
# advanced and secure methods: it's fine to store your secret key in your
# source code like we do here.
app.secret_key = 'Example Secret Key (CHANGE THIS TO YOUR OWN SECRET KEY!)'

# Set up database connection.
from loginapp import connect
from loginapp import db
db.init_db(app, connect.dbuser, connect.dbpass, connect.dbhost, connect.dbname,
           connect.dbport)

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

# Include all modules that define our Flask route-handling functions.
from loginapp import user
from loginapp import visitor
from loginapp import helper
from loginapp import admin
from loginapp import issues