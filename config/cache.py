"""
Cache Configuration
"""

import os

config = {
    'default': os.getenv('CACHE_DRIVER', 'file'),
    'prefix':  os.getenv('CACHE_PREFIX', 'laraflask_'),

    'stores': {
        'file': {
            'driver': 'file',
            'path':   'storage/cache/data',
        },
        'redis': {
            'driver':   'redis',
            'host':     os.getenv('REDIS_HOST', '127.0.0.1'),
            'port':     int(os.getenv('REDIS_PORT', 6379)),
            'password': os.getenv('REDIS_PASSWORD'),
            'database': 1,
        },
        'array': {
            'driver': 'array',
        },
        'database': {
            'driver': 'database',
            'table':  'cache',
        },
    },
}
