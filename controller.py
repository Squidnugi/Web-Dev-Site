from flask import Blueprint, request, redirect, url_for, session, flash, jsonify
from view import View
from model import Model
import secrets
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in') or session.get('account_type') != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

class Controller:
    def __init__(self, app):
        self.main_bp = Blueprint('main', __name__)
        self.routes()
        self.model = Model()
        app.register_blueprint(self.main_bp)
        app.secret_key = secrets.token_hex(32)
        self.ADMIN_CODE = 'admin123'

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
        self.main_bp.add_url_rule('/admin/user/<int:user_id>/delete', 'delete_user', self.delete_user, methods=['POST'])
        self.main_bp.add_url_rule('/admin/users/<int:user_id>/edit', 'update_user', self.update_user, methods=['POST', 'GET', 'PUT'])
        self.main_bp.add_url_rule('/sessions', 'sessions', self.sessions)
        self.main_bp.add_url_rule('/sessions/add', 'add_session', self.add_session, methods=['GET', 'POST'])
        self.main_bp.add_url_rule('/sessions/<int:session_id>/edit', 'edit_session', self.edit_session, methods=['GET', 'POST'])
        self.main_bp.add_url_rule('/sessions/delete/<int:session_id>', 'delete_session', self.delete_session, methods=['POST'])
        self.main_bp.add_url_rule('/contact', 'contact', self.contact, methods=['GET', 'POST'])
        self.main_bp.add_url_rule('/profile', 'profile', self.profile)
        self.main_bp.add_url_rule('/admindashboard', 'admindashboard', self.admindashboard, methods=['GET', 'POST'])
        self.main_bp.add_url_rule('/add_school', 'add_school', self.add_school, methods=['POST'])
        self.main_bp.add_url_rule('/api/sessions/<int:session_id>', 'api_get_session', self.get_session_api, methods=['GET'])
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
                session['account_type'] = user.account_type  # Store account type in session
                session['school_id'] = user.school_id
                return redirect(url_for('main.home'))
            else:
                flash('Invalid username or password', 'warning')
        return View.render_login()

    def signup(self):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            account_type = request.form['account_type']
            admin_code = request.form.get('admin_code')
            school_id = None

            # Extract the domain from the email
            domain = username.split('@')[-1]

            # Check if the domain is in the allowed list
            if account_type == 'supervisor':
                if domain not in self.model.supervisor_domain:
                    flash('Supervisor email domain is not recognised', 'danger')
                    return redirect(url_for('main.signup'))
            elif account_type == 'education':
                school_domains = self.model.get_domains()
                domain_info = next((item for item in school_domains if item['domain'] == domain), None)
                if not domain_info:
                    flash('School email domain is not recognised', 'danger')
                    return redirect(url_for('main.signup'))
                school_id = domain_info['id']
            elif account_type == 'admin':
                if admin_code != self.ADMIN_CODE:
                    flash('Invalid admin code', 'danger')
                    return redirect(url_for('main.signup'))
            if self.model.get_user_by_username(username):
                flash('Username already exists', 'error')
            else:
                self.model.create_user(username, password, account_type, school_id)
                flash('User created successfully', 'success')
                session['logged_in'] = True
                session['username'] = username
                session['account_type'] = account_type  # Store account type in session
                session['school_id'] = school_id
                return redirect(url_for('main.home'))
        return View.render_signup()

    def logout(self):
        session.pop('logged_in', None)
        session.pop('username', None)
        return redirect(url_for('main.home'))

    def sessions(self):
        if 'username' in session:
            account_type = session.get('account_type')
            username = session.get('username')

            # Get all sessions
            all_sessions = self.model.get_sessions()
            print(f"Total sessions: {len(all_sessions)}")  # Debug

            # Filter sessions for supervisors
            supervisor_data = None
            if account_type == 'supervisor':
                # Get supervisor data
                supervisors = self.model.get_supervisors()
                print(f"Supervisors: {supervisors}")  # Debug
                print(f"Looking for supervisor with email: {username}")  # Debug

                supervisor_data = next((s for s in supervisors if s['email'] == username), None)
                if supervisor_data:
                    print(f"Found supervisor: {supervisor_data}")  # Debug
                    # Only show sessions where the supervisor's email matches
                    filtered_sessions = [s for s in all_sessions if s['supervisor_email'] == username]
                    print(f"Filtered sessions: {len(filtered_sessions)}")  # Debug
                    all_sessions = filtered_sessions
                else:
                    print(f"No supervisor found with email: {username}")  # Debug
                    # No supervisor found, show empty list
                    all_sessions = []

            supervisors = self.model.get_supervisors()
            clients = self.model.get_clients()
            session_data = None

            # Check if session_id is provided
            session_id = request.args.get('session_id')
            if session_id:
                session_data = self.model.get_session(session_id)

            return View.render_sessions(all_sessions, session_data, supervisors, clients,
                                        is_supervisor=(account_type == 'supervisor'),
                                        supervisor_email=username if account_type == 'supervisor' else None,
                                        supervisor_data=supervisor_data)
        else:
            flash('You need to log in to view your sessions', 'warning')
            return redirect(url_for('main.login'))

    def add_session(self):
        if request.method == 'POST':
            try:
                # Create basic session data
                session_data = {
                    'client_id': request.form['client_id'],
                    'client_email': request.form['client_email'],
                    'date': request.form['date'],
                    'additional_info': request.form['additional_info']
                }

                # If supervisor, use their info directly
                if session.get('account_type') == 'supervisor':
                    # Get supervisor's user details from their email
                    supervisor_email = session.get('username')
                    supervisor = next((s for s in self.model.get_supervisors() if s['email'] == supervisor_email), None)

                    if not supervisor:
                        flash('Supervisor account not found', 'danger')
                        return redirect(url_for('main.sessions'))

                    session_data['supervisor_id'] = supervisor['id']
                    session_data['supervisor_email'] = supervisor_email
                else:
                    # For admins, use the selected supervisor
                    session_data['supervisor_id'] = request.form['supervisor_id']
                    session_data['supervisor_email'] = request.form['supervisor_email']

                self.model.create_session(session_data)
                flash('Session added successfully', 'success')
                return redirect(url_for('main.sessions'))
            except KeyError as e:
                flash(f'Missing form field: {e}', 'danger')
                return redirect(url_for('main.add_session'))
            except Exception as e:
                flash(f'An error occurred: {e}', 'danger')
                return redirect(url_for('main.add_session'))

        supervisors = self.model.get_supervisors()
        clients = self.model.get_clients()

        # If supervisor, find their details
        supervisor_data = None
        if session.get('account_type') == 'supervisor':
            supervisor_email = session.get('username')
            supervisor_data = next((s for s in supervisors if s['email'] == supervisor_email), None)

        return View.render_sessions_form(
            supervisors=supervisors,
            clients=clients,
            is_supervisor=(session.get('account_type') == 'supervisor'),
            supervisor_data=supervisor_data
        )

    def edit_session(self, session_id):
        if request.method == 'POST':
            try:
                # Get basic session data
                session_data = {
                    'client_id': request.form['client_id'],
                    'client_email': request.form['client_email'],
                    'date': request.form['date'],
                    'additional_info': request.form['additional_info']
                }

                # If supervisor, use their info directly
                if session.get('account_type') == 'supervisor':
                    supervisor_email = session.get('username')
                    supervisor = next((s for s in self.model.get_supervisors() if s['email'] == supervisor_email), None)

                    if not supervisor:
                        flash('Supervisor account not found', 'danger')
                        return redirect(url_for('main.sessions'))

                    session_data['supervisor_id'] = supervisor['id']
                    session_data['supervisor_email'] = supervisor_email
                else:
                    # For admins, use the selected supervisor
                    session_data['supervisor_id'] = request.form['supervisor_id']
                    session_data['supervisor_email'] = request.form['supervisor_email']

                self.model.update_session(session_id, session_data)
                flash('Session updated successfully', 'success')
                return redirect(url_for('main.sessions'))
            except KeyError as e:
                flash(f'Missing form field: {e}', 'danger')
                return redirect(url_for('main.edit_session', session_id=session_id))
            except Exception as e:
                flash(f'An error occurred: {e}', 'danger')
                return redirect(url_for('main.edit_session', session_id=session_id))

        session_data = self.model.get_session(session_id)
        supervisors = self.model.get_supervisors()
        clients = self.model.get_clients()

        # Get supervisor data for the form
        supervisor_data = None
        if session.get('account_type') == 'supervisor':
            supervisor_email = session.get('username')
            supervisor_data = next((s for s in supervisors if s['email'] == supervisor_email), None)

        return View.render_sessions_form(
            session_data=session_data,
            supervisors=supervisors,
            clients=clients,
            is_supervisor=(session.get('account_type') == 'supervisor'),
            supervisor_data=supervisor_data
        )

    def delete_session(self, session_id):
        self.model.delete_session(session_id)
        flash('Session deleted successfully', 'success')
        return redirect(url_for('main.sessions'))

    def contact(self):
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            message = request.form['message']
            try:
                self.model.add_contact(name, email, message)
                flash('Message sent successfully', 'success')
                return redirect(url_for('main.contact'))
            except Exception as e:
                flash(f'Error sending message: {str(e)}', 'danger')
                return redirect(url_for('main.contact'))
        return View.render_contact()

    def profile(self):
        return View.render_profile()

    @admin_required
    def admindashboard(self):
        users = self.model.get_all_users()
        return View.render_admindashboard(users=users)

    @admin_required
    def add_school(self):
        school_name = request.form['school_name']
        school_address = request.form['school_address']
        school_city = request.form['school_city']
        school_county = request.form['school_county']
        school_postcode = request.form['school_postcode']
        school_phone = request.form['school_phone']
        school_website = request.form['school_website']
        school_domain = request.form['school_domain']
        try:
            school_phone = int(school_phone)
        except ValueError:
            flash('School phone must be an integer', 'danger')
            return redirect(url_for('main.admindashboard'))
        self.model.create_school(school_name, school_address, school_city, school_county, school_postcode, school_phone, school_website, school_domain)
        flash('School added successfully', 'success')
        return redirect(url_for('main.admindashboard'))

    def get_session_api(self, session_id):
        # Make sure you're returning JSON
        session_data = self.model.get_session(session_id)
        if session_data:
            # Return as JSON
            return jsonify(session_data)
        else:
            return jsonify({"error": "Session not found"}), 404

    def delete_user(self, user_id):
        self.model.delete_user(user_id)
        flash('User deleted successfully', 'success')

    def update_user(self, user_id):
        user_data = {
            'email': request.form['email'],
            'password': request.form['password'],
            'account_type': request.form['account_type'],
            'school_id': request.form['school_id']
        }
        self.model.update_user(user_id, user_data)
        flash('User updated successfully', 'success')
        return redirect(url_for('main.users'))

    @admin_required
    def get_users(self):
        users = self.model.get_all_users()
        return jsonify(users)

    @admin_required
    def get_user(self, user_id):
        user = self.model.get_user(user_id)
        if user:
            return jsonify(user)
        else:
            return jsonify({"error": "User not found"}), 404

    @admin_required
    def edit_user(self, user_id):
        if request.method == 'POST':
            email = request.form['email']
            account_type = request.form['account_type']
            password = request.form['password'] if request.form['password'] else None

            try:
                self.model.update_user(user_id, email, account_type, password)
                flash('User updated successfully', 'success')
            except Exception as e:
                flash(f'Error updating user: {str(e)}', 'danger')

            return redirect(url_for('main.admindashboard'))

    @admin_required
    def delete_user(self, user_id):
        try:
            self.model.delete_user(user_id)
            return jsonify({"success": True}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500