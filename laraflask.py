#!/usr/bin/env python3
"""
Laraflask Application Entry Point

Run development server:
    python laraflask.py
    python laraflask.py --host=0.0.0.0 --port=8000

For production, use Gunicorn:
    gunicorn -w 4 -b 0.0.0.0:8000 laraflask:flask_app
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from laraflask.core.application import Application

# Create application instance
app = Application(os.path.dirname(os.path.abspath(__file__)))
app.bootstrap()

# Expose the Flask app for Gunicorn/uWSGI
flask_app = app.get_flask()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Laraflask Development Server')
    parser.add_argument('--host', default=os.getenv('APP_HOST', '127.0.0.1'))
    parser.add_argument('--port', type=int, default=int(os.getenv('APP_PORT', 8000)))
    args = parser.parse_args()

    app.run(host=args.host, port=args.port)
