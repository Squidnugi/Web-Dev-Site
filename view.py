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
        return render_template('signin.html')
