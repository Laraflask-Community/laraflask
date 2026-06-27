"""Filesystem / Storage Configuration"""
import os
config = {
    'default': os.getenv('FILESYSTEM_DISK', 'local'),
    'disks': {
        'local':  {'driver': 'local',  'root': 'storage/app',        'url': '/storage'},
        'public': {'driver': 'local',  'root': 'storage/app/public', 'url': '/storage', 'visibility': 'public'},
        's3':     {'driver': 's3',     'key': os.getenv('AWS_ACCESS_KEY_ID'), 'secret': os.getenv('AWS_SECRET_ACCESS_KEY'), 'region': os.getenv('AWS_DEFAULT_REGION', 'us-east-1'), 'bucket': os.getenv('AWS_BUCKET'), 'url': os.getenv('AWS_URL')},
        'minio':  {'driver': 's3',     'key': os.getenv('AWS_ACCESS_KEY_ID'), 'secret': os.getenv('AWS_SECRET_ACCESS_KEY'), 'region': 'us-east-1', 'bucket': os.getenv('AWS_BUCKET'), 'endpoint': os.getenv('AWS_ENDPOINT_URL')},
        'r2':     {'driver': 's3',     'key': os.getenv('AWS_ACCESS_KEY_ID'), 'secret': os.getenv('AWS_SECRET_ACCESS_KEY'), 'region': 'auto',      'bucket': os.getenv('AWS_BUCKET'), 'endpoint': os.getenv('AWS_ENDPOINT_URL')},
    },
}
