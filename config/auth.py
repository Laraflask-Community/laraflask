"""Authentication Configuration"""
import os
config = {
    'defaults': {'guard': 'web', 'passwords': 'users'},
    'guards': {
        'web': {'driver': 'session', 'provider': 'users'},
        'api': {'driver': 'jwt',     'provider': 'users', 'ttl': int(os.getenv('JWT_TTL', 60))},
    },
    'providers': {
        'users': {'driver': 'eloquent', 'model': 'app.Models.User.User'},
    },
    'passwords': {
        'users': {'provider': 'users', 'expire': 60, 'throttle': 60},
    },
}
