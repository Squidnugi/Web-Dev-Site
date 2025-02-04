from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from controller import Controller

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Register the controller
    Controller(app)

    return app