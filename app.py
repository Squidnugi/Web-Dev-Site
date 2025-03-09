from flask import Flask
from controller import Controller

# This function creates the Flask app
def create_app():
    app = Flask(__name__)

    # Register the controller
    Controller(app)


    return app