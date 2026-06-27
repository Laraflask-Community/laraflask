"""
Database Configuration
"""

import os

config = {
    'default': os.getenv('DB_CONNECTION', 'sqlite'),

    'connections': {
        'sqlite': {
            'driver':   'sqlite',
            'database': os.getenv('DB_DATABASE', 'database/laraflask.db'),
        },
        'mysql': {
            'driver':   'mysql',
            'host':     os.getenv('DB_HOST', '127.0.0.1'),
            'port':     os.getenv('DB_PORT', '3306'),
            'database': os.getenv('DB_DATABASE', 'laraflask'),
            'username': os.getenv('DB_USERNAME', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'charset':  'utf8mb4',
        },
        'postgresql': {
            'driver':   'postgresql',
            'host':     os.getenv('DB_HOST', '127.0.0.1'),
            'port':     os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_DATABASE', 'laraflask'),
            'username': os.getenv('DB_USERNAME', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
        },
    },

    'migrations': 'migrations',
    'pool_size': int(os.getenv('DB_POOL_SIZE', 5)),
    'pool_overflow': int(os.getenv('DB_POOL_OVERFLOW', 10)),
}
