import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback_secret_key'
    MONGODB_URI = os.environ.get('MONGODB_URI') or "mongodb://localhost:27017/database"

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    MONGODB_URI = os.environ.get('TEST_MONGODB_URI') or "mongodb://localhost:27017/test_database"

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    return config[os.environ.get('FLASK_ENV') or 'default']
