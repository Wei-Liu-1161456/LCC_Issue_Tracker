"""
Application initialization module.

This module initializes the Flask application, sets up the database connection,
and imports all route modules.
"""

from flask import Flask, url_for, session

app = Flask(__name__)

# Set the secret key for session management
app.secret_key = 'Wei Liu student ID: 1162456'

# Set up database connection
from loginapp import connect
from loginapp import db
db.init_db(app, connect.dbuser, connect.dbpass, connect.dbhost, connect.dbname,
           connect.dbport)

# Configure upload folder
app.config['UPLOAD_FOLDER'] = 'loginapp/static/uploads/profiles'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Import route modules
from loginapp import user
from loginapp import visitor
from loginapp import helper
from loginapp import admin
from loginapp import issues
from loginapp import utils  # 需要保留，因为它注册了模板全局函数