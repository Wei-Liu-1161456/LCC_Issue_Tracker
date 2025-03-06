"""
run.py

This module serves as the entry point for the Flask application. It imports the
Flask app instance from the loginapp module and runs the application.
"""

from loginapp import app

if __name__ == "__main__":
    """
    Main entry point for the application.

    This function runs the Flask application on the specified host and port.
    The application will be accessible from any IP address on port 5001.
    """
    app.run()