class WebControler:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def start(self):
        return self.view.show(self.model.check_login())