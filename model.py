from werkzeug.security import generate_password_hash, check_password_hash
import requests

# Class used to store school data
class School:
    def __init__(self, school_name, address, city, county, postcode, phone, website, domain):
        self.school_name = school_name
        self.address = address
        self.city = city
        self.county = county
        self.postcode = postcode
        self.phone = phone
        self.website = website
        self.domain = domain

    # Function to convert school data to a dictionary
    def to_dict(self):
        return {
            "name": self.school_name,
            "address": self.address,
            "city": self.city,
            "county": self.county,
            "postcode": self.postcode,
            "phone": self.phone,
            "website": self.website,
            "domain": self.domain
        }

# Class used to store user data and user related functions
class User:
    def __init__(self, email, password_hash, account_type, school_id):
        self.email = email
        self.password_hash = password_hash
        self.account_type = account_type
        self.school_id = school_id

    # Function to check if the password is correct
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Function to convert user data to a dictionary
    def to_dict(self):
        return {
            "email": self.email,
            "password": self.password_hash,
            "account_type": self.account_type,
            "school_id": self.school_id
        }

# This class is used to store the model and all the functions that interact with the API
class Model:
    def __init__(self):
        self.API_URL = "http://127.0.0.1:8000"
        self.supervisor_domain = 'example.com'
        self.TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

    # Function to authorize the requests
    def get_headers(self):
        return {"Authorization": f"Bearer {self.TOKEN}"}

    # Function to get a user by email
    def get_user_by_username(self, email):
        response = requests.get(f"{self.API_URL}/users/{email}", headers=self.get_headers())
        user = response.json()
        if 'email' in user:
            return User(user['email'], user['password'], user['account_type'], user['school_id'])
        else:
            print("Response JSON:", user)  # Debugging information
            return None

    # Function to add user to DB
    def create_user(self, email, password, account_type, school_id):
        password_hash = generate_password_hash(password)
        user = User(email, password_hash, account_type, school_id)
        requests.post(f"{self.API_URL}/users/", json=user.to_dict(), headers=self.get_headers())

    # Function to add school to DB
    def create_school(self, name, address, city, county, postcode, phone, website, domain):
        school_data = School(name, address, city, county, postcode, phone, website, domain)
        requests.post(f"{self.API_URL}/schools/", json=school_data.to_dict(), headers=self.get_headers())

    # Function to get all school domains
    def get_domains(self):
        response = requests.get(f"{self.API_URL}/schools/", headers=self.get_headers())
        schools = response.json()
        domains = [{'id': school['id'], 'domain': school['domain']} for school in schools if 'domain' in school]
        return domains

    # Function to add contact to DB
    def add_contact(self, name, email, message):
        contact_data = {
            "name": name,
            "email": email,
            "message": message
        }
        requests.post(f"{self.API_URL}/contact/", json=contact_data, headers=self.get_headers())

    # Function to get all contacts
    def get_contacts(self):
        response = requests.get(f"{self.API_URL}/contact/", headers=self.get_headers())
        return response.json()

    # Function to delete contact by ID
    def delete_contact(self, id):
        response = requests.delete(f"{self.API_URL}/contact/{id}", headers=self.get_headers())
        return response.status_code == 204

    # Function to get all sessions by email
    def get_sessions_by_username(self, email):
        response = requests.get(f"{self.API_URL}/sessions/{email}", headers=self.get_headers())
        return response.json()

    # Function to get all sessions by a school
    def get_sessions_by_school(self, school_id):
        response = requests.get(f"{self.API_URL}/sessions/school/{school_id}", headers=self.get_headers())
        return response.json()

    # Function to get all sessions
    def get_sessions(self):
        response = requests.get(f"{self.API_URL}/sessions/", headers=self.get_headers())
        return response.json()

    # Function to add session to DB
    def create_session(self, session_data):
        # If client is education type, get and add school info
        if 'client_id' in session_data:
            client_id = session_data['client_id']
            # Get client info to check account type
            response = requests.get(f"{self.API_URL}/users/{client_id}", headers=self.get_headers())

            # Check if the client exists
            if response.status_code == 404:
                print(f"Client ID {client_id} not found. Creating session without school info.")
            else:
                client = response.json()
                if client.get('account_type') == 'education' and client.get('school_id'):
                    # Add school_id to session data
                    session_data['school_id'] = client['school_id']

        # Create the session with whatever data we have
        response = requests.post(f"{self.API_URL}/sessions/", json=session_data, headers=self.get_headers())
        return response.json()

    # Function to update session by ID
    def update_session(self, session_id, session_data):
        response = requests.put(f"{self.API_URL}/sessions/{session_id}", json=session_data, headers=self.get_headers())
        return response.json()

    # Function to delete session by ID
    def delete_session(self, session_id):
        response = requests.delete(f"{self.API_URL}/sessions/{session_id}", headers=self.get_headers())
        return response.status_code == 204

    # Function to get session by ID
    def get_session(self, session_id):
        response = requests.get(f"{self.API_URL}/sessions/{session_id}", headers=self.get_headers())
        return response.json()

    # Function to get all supervisors
    def get_supervisors(self):
        response = requests.get(f"{self.API_URL}/users", headers=self.get_headers())
        users = response.json()
        supervisors = [user for user in users if user['account_type'] == 'supervisor']
        return supervisors

    # Function to get all clients
    def get_clients(self):
        response = requests.get(f"{self.API_URL}/users", headers=self.get_headers())
        users = response.json()
        clients = [user for user in users if user['account_type'] in ['education', 'other']]
        return clients

    # Function to delete user by ID
    def delete_user(self, user_id):
        response = requests.delete(f"{self.API_URL}/users/{user_id}", headers=self.get_headers())
        return response.status_code == 204

    # Function to get all users
    def get_all_users(self):
        response = requests.get(f"{self.API_URL}/users", headers=self.get_headers())
        return response.json()

    # Function to get school by ID
    def get_school(self, school_id):
        response = requests.get(f"{self.API_URL}/schools/{school_id}", headers=self.get_headers())
        return response.json()

    # Function to delete school by ID
    def delete_school(self, school_id):
        response = requests.delete(f"{self.API_URL}/schools/{school_id}", headers=self.get_headers())
        return response.status_code == 204

    # Function to update school by ID
    def update_school(self, school_id, school_data):
        response = requests.put(f"{self.API_URL}/schools/{school_id}", json=school_data, headers=self.get_headers())
        return response.json()

    # Function to get all schools
    def get_schools(self):
        response = requests.get(f"{self.API_URL}/schools/", headers=self.get_headers())
        return response.json()