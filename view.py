from flask import render_template

class View:
    @staticmethod
    def render_home():
        return render_template('home.html')

    @staticmethod
    def render_about():
        return render_template('about.html')

    @staticmethod
    def render_user(user):
        return render_template('user.html', user=user)

    @staticmethod
    def render_login():
        return render_template('login.html')

    @staticmethod
    def render_signup():
        return render_template('signup.html')

    @staticmethod
    def render_sessions(sessions, session_data=None, supervisors=None, clients=None,
                        is_supervisor=False, supervisor_email=None, supervisor_data=None,
                        is_client=False, client_data=None, current_filter='all'):
        return render_template(
            'sessions.html',
            sessions=sessions,
            session_data=session_data,
            supervisors=supervisors,
            clients=clients,
            is_supervisor=is_supervisor,
            supervisor_email=supervisor_email,
            supervisor_data=supervisor_data,
            is_client=is_client,
            client_data=client_data,
            current_filter=current_filter
        )

    @staticmethod
    def render_sessions_form(session_data=None, supervisors=None, clients=None, is_supervisor=False,
                             supervisor_data=None, is_client=False, client_data=None):
        return render_template('session_form.html',
                               session_data=session_data,
                               supervisors=supervisors,
                               clients=clients,
                               is_supervisor=is_supervisor,
                               supervisor_data=supervisor_data,
                               is_client=is_client,
                               client_data=client_data)
    
    @staticmethod
    def render_contact():
        return render_template('contact.html')

    @staticmethod
    def render_profile():
        return render_template('profile.html')

    @staticmethod
    def render_admindashboard(users=None, contacts=None, schools=None):
        return render_template(
            'admin-dash.html',
            users=users,
            contacts=contacts,
            schools=schools,
            title='Admin Dashboard'
        )

