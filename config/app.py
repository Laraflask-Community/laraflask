"""
Application Configuration
"""

import os

config = {
    'name':     os.getenv('APP_NAME', 'Laraflask'),
    'env':      os.getenv('APP_ENV', 'production'),
    'debug':    os.getenv('APP_DEBUG', 'false').lower() == 'true',
    'url':      os.getenv('APP_URL', 'http://localhost:8000'),
    'timezone': os.getenv('APP_TIMEZONE', 'UTC'),
    'locale':   os.getenv('APP_LOCALE', 'en'),
    'key':      os.getenv('APP_KEY', ''),

    'providers': [
        # Application Service Providers
        # 'app.Providers.AppServiceProvider.AppServiceProvider',
        # 'app.Providers.AuthServiceProvider.AuthServiceProvider',
        # 'app.Providers.EventServiceProvider.EventServiceProvider',
        # 'app.Providers.RouteServiceProvider.RouteServiceProvider',
    ],

    'aliases': {
        'Auth':     'laraflask.auth.auth.Auth',
        'Cache':    'laraflask.cache.cache.Cache',
        'DB':       'laraflask.orm.db.DB',
        'Events':   'laraflask.events.dispatcher.Events',
        'Gate':     'laraflask.auth.auth.Gate',
        'Hash':     'laraflask.auth.auth.Hash',
        'Queue':    'laraflask.queue.queue.Queue',
        'Schedule': 'laraflask.scheduler.schedule.Schedule',
        'Schema':   'laraflask.orm.migration.Schema',
        'Storage':  'laraflask.storage.storage.Storage',
    },
}
