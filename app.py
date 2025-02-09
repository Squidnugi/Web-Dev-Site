from flask import Flask
from controller import Controller


def create_app():
    app = Flask(__name__)

    # Register the controller
    Controller(app)

    return app