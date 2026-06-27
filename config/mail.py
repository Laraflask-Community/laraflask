"""Mail Configuration"""
import os
config = {
    'default': os.getenv('MAIL_MAILER', 'smtp'),
    'mailers': {
        'smtp': {
            'transport':  'smtp',
            'host':       os.getenv('MAIL_HOST', 'smtp.mailtrap.io'),
            'port':       int(os.getenv('MAIL_PORT', 2525)),
            'encryption': os.getenv('MAIL_ENCRYPTION', 'tls'),
            'username':   os.getenv('MAIL_USERNAME'),
            'password':   os.getenv('MAIL_PASSWORD'),
        },
    },
    'from': {
        'address': os.getenv('MAIL_FROM_ADDRESS', 'hello@laraflask.dev'),
        'name':    os.getenv('MAIL_FROM_NAME', 'Laraflask'),
    },
}
