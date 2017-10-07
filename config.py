"""
settings,
environment variables to set:
SECRET_KEY,
REG_MAIL_PASSWORD
"""

import os
BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """
    common config settings
    """
    QOTES_ADMIN = 'sy@qotes.top'
    SECRET_KEY = os.environ.get('CSRFKEY') or 'Q0t1s'
    # I'm just pretenting that I'm using it :)
    MONGODB_SETTINGS = {
        'db': 'qotes',
        'host': '127.0.0.1',
        'port': 27017,
        'user': 'qotes',
        'password': os.environ.get('QOTES_MONGO_PASSWORD') or 'qotes'
    }
    # mail
    MAIL_USERNAME = os.environ.get('QOTES_MAIL_USERNAME') or 'check@qotes.top'
    MAIL_PASSWORD = os.environ.get('QOTES_MAIL_PASSWORD')
    MAIL_SERVER = os.environ.get('QOTES_MAIL_SERVER') or 'smtp.mxhichina.com'
    MAIL_PORT = os.environ.get('QOTES_MAIL_SERVER') or 25  #tls465
    MAIL_USE_TLS = False

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    """
    settings for developing
    """
    DEBUG = True


config = {
    'dev': DevConfig,
    'default': DevConfig,
}
