from flask import Blueprint, request, redirect, url_for, session, flash, jsonify
from view import View
from model import Model
import secrets
from functools import wraps

# Decorator to require admin access
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in') or session.get('account_type') != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator to check if user is logged in
def login_check(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('You need to log in to access this page.', 'warning')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

# This class is responsible for handling the routes and requests
class Controller:
    def __init__(self, app):
        self.model = Model()
        self.view = View
        self.main_bp = Blueprint('main', __name__)
        self.routes()
        app.register_blueprint(self.main_bp)
        app.secret_key = secrets.token_hex(32)
        self.ADMIN_CODE = 'admin123'

    # Function to define the routes
    def routes(self):
        self.main_bp.add_url_rule('/', 'home', self.view.render_home)
        self.main_bp.add_url_rule('/about', 'about', self.view.render_about)
        self.main_bp.add_url_rule('/login', 'login', self.login, methods=['GET', 'POST'])
        self.main_bp.add_url_rule('/signup', 'signup', self.signup, methods=['GET', 'POST'])
        self.main_bp.add_url_rule('/logout', 'logout', self.logout)
        self.main_bp.add_url_rule('/admin/user/<int:user_id>/delete', 'delete_user', self.delete_user, methods=['POST', 'GET'])
        self.main_bp.add_url_rule('/sessions', 'sessions', self.sessions)
        self.main_bp.add_url_rule('/sessions/add', 'add_session', self.add_session, methods=['GET', 'POST'])
        self.main_bp.add_url_rule('/sessions/<int:session_id>/edit', 'edit_session', self.edit_session, methods=['GET', 'POST'])
        self.main_bp.add_url_rule('/sessions/<int:session_id>/delete', 'delete_session', self.delete_session, methods=['POST', 'GET', 'DELETE'])
        self.main_bp.add_url_rule('/contact', 'contact', self.contact, methods=['GET', 'POST'])
        self.main_bp.add_url_rule('/admindashboard', 'admindashboard', self.admindashboard, methods=['GET', 'POST'])
        self.main_bp.add_url_rule('/add_school', 'add_school', self.add_school, methods=['POST'])
        self.main_bp.add_url_rule('/api/sessions/<int:session_id>', 'api_get_session', self.get_session_api, methods=['GET'])
        self.main_bp.add_url_rule('/admin/contact/<int:contact_id>/delete', 'delete_contact', self.delete_contact_admin, methods=['POST', 'GET', 'DELETE'])
        self.main_bp.add_url_rule('/admin/school/<int:school_id>/delete', 'delete_school', self.delete_school, methods=['POST', 'GET'])
        self.main_bp.add_url_rule('/admin/school/<int:school_id>/edit', 'edit_school', self.edit_school, methods=['POST', 'GET'])
        self.main_bp.add_url_rule('/admin/schools/<int:school_id>', 'api_get_school', self.get_school_api, methods=['GET'])


    # Function to handle login
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
                flash('Logged in successfully', 'success')
                return redirect(url_for('main.home'))
            else:
                flash('Invalid username or password', 'warning')
        return self.view.render_login()

    # Function to handle signup
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
        return self.view.render_signup()

    # Function to handle logout
    @login_check
    def logout(self):
        session.pop('logged_in', None)
        session.pop('username', None)
        flash('Logged out successfully', 'success')
        return redirect(url_for('main.home'))

    # Function to handle sessions
    @login_check
    def sessions(self):
        if 'username' in session:
            account_type = session.get('account_type')
            username = session.get('username')
            filter_type = request.args.get('filter', 'all')  # Default filter is 'all'

            # Get all sessions
            all_sessions = self.model.get_sessions()

            # Filter sessions based on user type
            # Filter sessions based on user type
            if account_type == 'supervisor':
                # For supervisors, only show their own sessions
                filtered_sessions = [s for s in all_sessions if s['supervisor_email'] == username]

                # Apply additional filtering for supervisors if requested
                if filter_type == 'education':
                    # Get all education clients
                    clients = self.model.get_clients()
                    education_clients = [c for c in clients if c.get('account_type') == 'education']
                    client_ids = [c['id'] for c in education_clients]
                    filtered_sessions = [s for s in filtered_sessions if s['client_id'] in client_ids]
                elif filter_type == 'other':
                    # Get all non-education clients
                    clients = self.model.get_clients()
                    other_clients = [c for c in clients if c.get('account_type') == 'other']
                    client_ids = [c['id'] for c in other_clients]
                    filtered_sessions = [s for s in filtered_sessions if s['client_id'] in client_ids]

                all_sessions = filtered_sessions

                # Get supervisor data
                supervisors = self.model.get_supervisors()
                supervisor_data = next((s for s in supervisors if s['email'] == username), None)
            elif account_type == 'education':
                # For education users, only show sessions related to their school
                school_id = session.get('school_id')
                # Assuming sessions have a school_id field or clients have a school_id field
                # You'll need to adapt this to your data structure
                filtered_sessions = []
                clients = self.model.get_clients()
                school_clients = [c for c in clients if c.get('school_id') == school_id]
                client_ids = [c['id'] for c in school_clients]
                filtered_sessions = [s for s in all_sessions if s['client_id'] in client_ids]
                all_sessions = filtered_sessions
                supervisor_data = None
            elif account_type == 'other':
                filtered_sessions = [s for s in all_sessions if s['client_email'] == username]
                all_sessions = filtered_sessions
                # For other account types, show only sessions where they're the client
                supervisor_data = None

            else:
                # For admin users, apply filtering if requested
                if filter_type == 'education':
                    # Get all education clients
                    clients = self.model.get_clients()
                    education_clients = [c for c in clients if c.get('account_type') == 'education']
                    client_ids = [c['id'] for c in education_clients]
                    filtered_sessions = [s for s in all_sessions if s['client_id'] in client_ids]
                    all_sessions = filtered_sessions
                elif filter_type == 'other':
                    # Get all non-education clients
                    clients = self.model.get_clients()
                    other_clients = [c for c in clients if c.get('account_type') != 'education']
                    client_ids = [c['id'] for c in other_clients]
                    filtered_sessions = [s for s in all_sessions if s['client_id'] in client_ids]
                    all_sessions = filtered_sessions
                supervisor_data = None

            supervisors = self.model.get_supervisors()
            clients = self.model.get_clients()
            session_data = None

            # Check if session_id is provided
            session_id = request.args.get('session_id')
            if session_id:
                session_data = self.model.get_session(session_id)

            return self.view.render_sessions(
                all_sessions,
                session_data,
                supervisors,
                clients,
                is_supervisor=(account_type == 'supervisor'),
                supervisor_email=username if account_type == 'supervisor' else None,
                supervisor_data=supervisor_data,
                is_client=True if session.get('account_type') in ['education', 'other'] else False,
                current_filter=filter_type
            )
        else:
            flash('You need to log in to view your sessions', 'warning')
            return redirect(url_for('main.login'))

    # Funtion to add a session
    @login_check
    def add_session(self):
        if request.method == 'POST':
            try:
                # Create basic session data
                session_data = {
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

                    # For supervisors, we still need to get client from form
                    session_data['client_id'] = request.form['client_id']
                    session_data['client_email'] = request.form['client_email']

                # If education or other (clients), use their info directly
                elif session.get('account_type') in ['education', 'other']:
                    client_email = session.get('username')
                    client = next((c for c in self.model.get_clients() if c['email'] == client_email), None)

                    if not client:
                        flash('Client account not found', 'danger')
                        return redirect(url_for('main.sessions'))

                    session_data['client_id'] = client['id']
                    session_data['client_email'] = client_email

                    # For clients, we still need to get supervisor from form
                    session_data['supervisor_id'] = request.form['supervisor_id']
                    session_data['supervisor_email'] = request.form['supervisor_email']

                else:
                    # For admins, use the selected supervisor and client
                    session_data['supervisor_id'] = request.form['supervisor_id']
                    session_data['supervisor_email'] = request.form['supervisor_email']
                    session_data['client_id'] = request.form['client_id']
                    session_data['client_email'] = request.form['client_email']

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

        # If client (education or other), find their details
        client_data = None
        if session.get('account_type') in ['education', 'other']:
            client_email = session.get('username')
            client_data = next((c for c in clients if c['email'] == client_email), None)

        return self.view.render_sessions_form(
            supervisors=supervisors,
            clients=clients,
            is_supervisor=(session.get('account_type') == 'supervisor'),
            supervisor_data=supervisor_data,
            is_client=True if session.get('account_type') in ['education', 'other'] else False,
            client_data=client_data
        )

    # Function to edit a session
    @login_check
    def edit_session(self, session_id):
        if request.method == 'POST':
            try:
                # Get basic session data
                session_data = {
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

                    # For supervisors, we still need to get client from form
                    session_data['client_id'] = request.form['client_id']
                    session_data['client_email'] = request.form['client_email']

                # If education or other (clients), use their info directly
                elif session.get('account_type') in ['education', 'other']:
                    client_email = session.get('username')
                    client = next((c for c in self.model.get_clients() if c['email'] == client_email), None)

                    if not client:
                        flash('Client account not found', 'danger')
                        return redirect(url_for('main.sessions'))

                    session_data['client_id'] = client['id']
                    session_data['client_email'] = client_email

                    # For clients, we still need to get supervisor from form
                    session_data['supervisor_id'] = request.form['supervisor_id']
                    session_data['supervisor_email'] = request.form['supervisor_email']

                else:
                    # For admins, use the selected supervisor and client
                    session_data['supervisor_id'] = request.form['supervisor_id']
                    session_data['supervisor_email'] = request.form['supervisor_email']
                    session_data['client_id'] = request.form['client_id']
                    session_data['client_email'] = request.form['client_email']

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

        # Get client data for the form
        client_data = None
        if session.get('account_type') in ['education', 'other']:
            client_email = session.get('username')
            client_data = next((c for c in clients if c['email'] == client_email), None)

        return self.view.render_sessions_form(
            session_data=session_data,
            supervisors=supervisors,
            clients=clients,
            is_supervisor=(session.get('account_type') == 'supervisor'),
            supervisor_data=supervisor_data,
            is_client=True if session.get('account_type') in ['education', 'other'] else False,
            client_data=client_data
        )

    # Function to delete a session
    @login_check
    def delete_session(self, session_id):
        self.model.delete_session(session_id)
        flash('Session deleted successfully', 'success')
        return redirect(url_for('main.sessions'))

    # Function to handle contact form
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
        return self.view.render_contact()


    # Function to handle admin dashboard
    @admin_required
    def admindashboard(self):
        users = self.model.get_all_users()
        contacts = self.model.get_contacts()
        schools = self.model.get_schools()  # Add this line to get schools
        return self.view.render_admindashboard(users=users, contacts=contacts, schools=schools)

    # Function to handle admin contact deletion
    @admin_required
    def delete_contact_admin(self, contact_id):
        try:
            self.model.delete_contact(contact_id)
            flash('Contact deleted successfully', 'success')
            return redirect(url_for('main.admindashboard'))
        except Exception as e:
            flash(f'Error deleting contact: {str(e)}', 'danger')
            return redirect(url_for('main.admindashboard'))

    # Function to handle school addition
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

    # Function to delete a school
    @admin_required
    def delete_school(self, school_id):
        try:
            self.model.delete_school(school_id)
            flash('School deleted successfully', 'success')
            return redirect(url_for('main.admindashboard'))
        except Exception as e:
            flash(f'Error deleting school: {str(e)}', 'danger')
            return redirect(url_for('main.admindashboard'))

    # Function to edit a school
    @admin_required
    def edit_school(self, school_id):
        if request.method == 'POST':
            school_data = {
                'name': request.form['school_name'],
                'address': request.form['school_address'],
                'city': request.form['school_city'],
                'county': request.form['school_county'],
                'postcode': request.form['school_postcode'],
                'phone': request.form['school_phone'],
                'website': request.form['school_website'],
                'domain': request.form['school_domain']
            }
            self.model.update_school(school_id, school_data)
            flash('School updated successfully', 'success')
            return redirect(url_for('main.admindashboard'))

    # Function to get a session by ID
    @login_check
    def get_session_api(self, session_id):
        # Make sure you're returning JSON
        session_data = self.model.get_session(session_id)
        if session_data:
            # Return as JSON
            return jsonify(session_data)
        else:
            return jsonify({"error": "Session not found"}), 404

    # Function to delete a user
    @admin_required
    def delete_user(self, user_id):
        try:
            self.model.delete_user(user_id)
            flash('User deleted successfully', "success")
            return redirect(url_for('main.admindashboard'))
        except Exception as e:
            flash(f'Error deleting user: {str(e)}', 'danger')
            return redirect(url_for('main.admindashboard'))

    # Function to get school by ID
    @admin_required
    def get_school_api(self, school_id):
        school_data = self.model.get_school(school_id)
        if school_data:
            return jsonify(school_data)
        else:
            return jsonify({"error": "School not found"}), 404