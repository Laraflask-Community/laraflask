"""Session Configuration"""
import os
config = {
    'driver':    os.getenv('SESSION_DRIVER', 'filesystem'),
    'lifetime':  int(os.getenv('SESSION_LIFETIME', 120)),
    'path':      '/',
    'cookie':    os.getenv('SESSION_COOKIE', 'laraflask_session'),
    'secure':    os.getenv('SESSION_SECURE_COOKIE', 'false').lower() == 'true',
    'http_only': True,
    'same_site': 'lax',
}
