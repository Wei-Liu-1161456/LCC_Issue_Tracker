from flask import Flask, g
import MySQLdb

# Database connection parameters (set when calling `init_db`).
connection_params = {}

def init_db(app: Flask, user: str, password: str, host: str, database: str,
            port: int = 3306, autocommit: bool = True):
    """Sets up MySQL connectivity for the specified Flask app.

    This must be called once while initialising your Flask web app, before any
    other `db` module functions are called.

    Args:
        app: The `Flask` application to set up database connectivity for.
        user: Username used to connect to the MySQL server.
        password: Password used to connect to the MySQL server.
        host: Host name or IP address of the MySQL server.
        database: Name of the database to connect to on the MySQL server.
        port: Port used to connect to the MySQL server (default `3306`).
        autocommit: Whether or not to enable auto-commit (default `True`) .
    """
    # Save connection details.
    connection_params['user'] = user
    connection_params['password'] = password
    connection_params['host'] = host
    connection_params['database'] = database
    connection_params['port'] = port
    connection_params['autocommit'] = autocommit

    # Register `close_db()` to run every time the application context is torn
    # down at the end of a Flask request, ensuring that any database connection
    # using during that request gets closed.
    app.teardown_appcontext(close_db)

def get_db():
    """Gets a MySQL database connection to use while serving the current Flask
    request.

    The first time you call this during a request, a new connection will be
    created. After that, any additional calls to `get_db()` during the same
    request are guaranteed to return the same connection.
    
    If you only need a MySQL cursor, and not a reference to the database, you
    can just call the `get_cursor()` function. There's no need to call
    `get_db()` first.

    You don't need to manually close the connection returned by `get_db()` - it
    will be closed automatically at the end of the Flask request. However, you
    should be sure to close any cursors that you create, including any created
    by the `get_cursor()` function.

    Returns:
        A `Connection` instance.
    """
    if 'db' not in g:
        g.db = MySQLdb.connect(**connection_params)

    return g.db

def get_cursor():
    """Gets a new MySQL dictionary cursor to use while serving the current
    Flask request.
    
    All cursors created by this function during a single Flask request will
    belong to the same connection. You can get a reference to that connection
    at any time during the request by calling `get_db()`.
    
    Ensure that you close all cursors before the end of the Flask request.
    
    Returns:
        A new `MySQLdb.cursors.DictCursor` instance.
    """
    return get_db().cursor(cursorclass=MySQLdb.cursors.DictCursor)

def close_db(exception = None):
    """Closes the MySQL database connection associated with the current Flask
    request (if any).
    
    There should be no need to call this manually: this function is called
    automatically when the application context is torn down at the end of each
    Flask request.

    Args:
        exception: The exception that terminated the Flask request, or `None`
            if the request terminated successfully.
    """
    # Get the database connection from the current application context (the one
    # that's being torn down), or `None` if there is no connection.
    db = g.pop('db', None)
    
    if db is not None:
        db.close()