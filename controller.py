from flask import Blueprint, request, redirect, url_for, session, flash
from view import View
from model import Model

class Controller:
    def __init__(self, app):
        self.main_bp = Blueprint('main', __name__)
        self.routes()
        self.model = Model()
        app.register_blueprint(self.main_bp)
        app.secret_key = 'your_secret_key'

    def routes(self):
        self.main_bp.add_url_rule('/', 'home', View.render_home)
        self.main_bp.add_url_rule('/about', 'about', View.render_about)
        self.main_bp.add_url_rule('/user', 'users', self.get_users)
        self.main_bp.add_url_rule('/user/<int:user_id>', 'user', self.get_user)
        self.main_bp.add_url_rule('/login', 'login', self.login, methods=['GET', 'POST'])
        self.main_bp.add_url_rule('/signup', 'signup', self.signup, methods=['GET', 'POST'])
        self.main_bp.add_url_rule('/logout', 'logout', self.logout)
    
    def get_users(self):
        return View.render_user(self.model.getusers())
    
    def get_user(self, user_id):
        user = self.model.getuser(user_id)
        return View.render_user(user)

    def login(self):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = self.model.get_user_by_username(username)
            if user and user.check_password(password):
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('main.home'))
            else:
                flash('Invalid username or password')
        return View.render_login()

    def signup(self):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if self.model.get_user_by_username(username):
                flash('Username already exists')
            else:
                self.model.create_user(username, password)
                flash('User created successfully')
                return redirect(url_for('main.login'))
        return View.render_signup()

    def logout(self):
        session.pop('logged_in', None)
        session.pop('username', None)
        return redirect(url_for('main.home'))