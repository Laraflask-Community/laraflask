#!/usr/bin/env python3
"""
ArtisanPy — The Laraflask Command Line Interface

Usage:
    python artisan.py <command> [options] [arguments]

Examples:
    python artisan.py make:model User -m -c -r
    python artisan.py make:controller UserController --resource
    python artisan.py make:migration create_users_table
    python artisan.py migrate
    python artisan.py migrate:rollback --step=2
    python artisan.py migrate:fresh
    python artisan.py db:seed
    python artisan.py queue:work --queue=default --sleep=3
    python artisan.py schedule:run
    python artisan.py cache:clear
    python artisan.py route:list
    python artisan.py serve --host=127.0.0.1 --port=8000
    python artisan.py key:generate
    python artisan.py about
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment before anything else
from dotenv import load_dotenv
load_dotenv()

from laraflask.console.artisan import ArtisanPy


def main():
    artisan = ArtisanPy()
    exit_code = artisan.run(sys.argv[1:])
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
