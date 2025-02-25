from werkzeug.security import generate_password_hash, check_password_hash
import requests

class User:
    def __init__(self, email, password_hash):
        self.email = email
        self.password_hash = password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "email": self.email,
            "password": self.password_hash
        }

class Model:
    def __init__(self):
        self.BASE_URL = "http://127.0.0.1:8000"

    def get_user_by_username(self, email):
        response = requests.get(f"{self.BASE_URL}/users/{email}")
        user = response.json()
        if 'email' in user:
            return User(user['email'], user['password'])
        else:
            print("Response JSON:", user)  # Debugging information
            return None

    def create_user(self, email, password):
        password_hash = generate_password_hash(password)
        user = User(email, password_hash)
        requests.post(f"{self.BASE_URL}/users/", json=user.to_dict())