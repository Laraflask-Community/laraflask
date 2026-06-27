"""Queue Configuration"""
import os
config = {
    'default': os.getenv('QUEUE_CONNECTION', 'sync'),
    'connections': {
        'sync':     {'driver': 'sync'},
        'database': {'driver': 'database', 'table': 'jobs', 'retry_after': 90},
        'redis':    {'driver': 'redis',    'connection': 'default', 'queue': 'default', 'retry_after': 90},
    },
    'failed': {'driver': 'database', 'table': 'failed_jobs'},
}
