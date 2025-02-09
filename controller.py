from flask import Blueprint
from view import View
from model import Model

class Controller:
    def __init__(self, app):
        self.main_bp = Blueprint('main', __name__)
        self.routes()
        app.register_blueprint(self.main_bp)

    def routes(self):
        self.main_bp.add_url_rule('/', 'home', View.render_home)
        self.main_bp.add_url_rule('/about', 'about', View.render_about)
