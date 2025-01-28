class WebModule:
    def __init__(self):
        self.log = False

    def check_login(self):
        return self.log

    def get_login(self):
        self.log = True
        return self.log