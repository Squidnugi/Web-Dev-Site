from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Model:
    def __init__(self):
        self.users = {}

    def get_user_by_username(self, username):
        return self.users.get(username)

    def create_user(self, username, password):
        password_hash = generate_password_hash(password)
        self.users[username] = User(username, password_hash)