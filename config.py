import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False # API Mode

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    pass

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Ensure cookies work across ports (CORS) but only on same-site (Lax is good for 127.0.0.1)
Config.SESSION_COOKIE_SAMESITE = 'Lax'
Config.SESSION_COOKIE_SECURE = False   # Set to True in Production with HTTPS
Config.REMEMBER_COOKIE_SAMESITE = 'Lax'
Config.REMEMBER_COOKIE_SECURE = False
