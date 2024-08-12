from flask import Flask
from flask_pymongo import PyMongo

mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    mongo.init_app(app)
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
