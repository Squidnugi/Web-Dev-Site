from flask import Blueprint, request, redirect, url_for, session, flash
from view import View
from model import Model
import secrets
from flask_mail import Mail, Message


class Controller:
    def __init__(self, app):
        self.main_bp = Blueprint('main', __name__)
        self.routes()
        self.model = Model()
        app.register_blueprint(self.main_bp)
        app.secret_key = secrets.token_hex(32)

        # Configure Flask-Mail
        # app.config['MAIL_SERVER'] = 'smtp.example.com'
        # app.config['MAIL_PORT'] = 587
        # app.config['MAIL_USE_TLS'] = True
        # app.config['MAIL_USERNAME'] = 'your-email@example.com'
        # app.config['MAIL_PASSWORD'] = 'your-email-password'
        # app.config['TESTING'] = True
        # self.mail = Mail(app)

    def routes(self):
        self.main_bp.add_url_rule('/', 'home', View.render_home)
        self.main_bp.add_url_rule('/about', 'about', View.render_about)
        self.main_bp.add_url_rule('/user', 'users', self.get_users)
        self.main_bp.add_url_rule('/user/<int:user_id>', 'user', self.get_user)
        self.main_bp.add_url_rule('/login', 'login', self.login, methods=['GET', 'POST'])
        self.main_bp.add_url_rule('/signup', 'signup', self.signup, methods=['GET', 'POST'])
        self.main_bp.add_url_rule('/logout', 'logout', self.logout)
        #self.main_bp.add_url_rule('/user/<int:user_id>', 'delete_user', self.delete_user, methods=['DELETE'])
        #self.main_bp.add_url_rule('/user/<int:user_id>', 'update_user', self.update_user, methods=['PUT'])
        self.main_bp.add_url_rule('/sessions', 'sessions', self.sessions)
        self.main_bp.add_url_rule('/contact', 'contact', self.contact, methods=['GET', 'POST'])
        self.main_bp.add_url_rule('/profile', 'profile', self.profile)
        self.main_bp.add_url_rule('/admindashboard', 'admindashboard', self.admindashboard, methods=['GET', 'POST'])

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
                flash('Invalid username or password', 'warning')
        return View.render_login()

    def signup(self):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            account_type = request.form['account_type']
            if self.model.get_user_by_username(username):
                flash('Username already exists', 'error')
            elif account_type.lower() == 'admin':
                flash('Invalid account type', 'warning')
            else:
                self.model.create_user(username, password, account_type)
                flash('User created successfully', 'success')
                return redirect(url_for('main.login'))
        return View.render_signup()

    def logout(self):
        session.pop('logged_in', None)
        session.pop('username', None)
        return redirect(url_for('main.home'))
    
    def sessions(self):
        return View.render_sessions()

    def contact(self):
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            message = request.form['message']
            # Send email
            # msg = Message('Contact Form Submission',
            #               sender='your-email@example.com',
            #               recipients=['recipient@example.com'])
            # msg.body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
            # self.mail.send(msg)
            flash('Message sent successfully', 'success')
            return redirect(url_for('main.contact'))
        return View.render_contact()

    def profile(self):
        return View.render_profile()
    
    def admindashboard(self):
        return View.render_admindashboard()