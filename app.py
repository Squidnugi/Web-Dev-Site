from flask import Flask, render_template
from controler import WebControler
from view import WebView
from module import WebModule
app = Flask(__name__)
view = WebView()
module = WebModule()
controller = WebControler(module, view)

@app.route('/')
def hello_world():
    return render_template(controller.start())

@app.route('/submit')
def submit():
    return render_template()
if __name__ == '__main__':
    app.run()
