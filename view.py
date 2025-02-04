from flask import render_template

class View:
    @staticmethod
    def render_home():
        return render_template('home.html')

    @staticmethod
    def render_about():
        return render_template('about.html')
