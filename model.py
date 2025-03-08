from werkzeug.security import generate_password_hash, check_password_hash
import requests

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


class User:
    def __init__(self, email, password_hash, account_type, school_id):
        self.email = email
        self.password_hash = password_hash
        self.account_type = account_type
        self.school_id = school_id


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def to_dict(self):
        return {
            "email": self.email,
            "password": self.password_hash,
            "account_type": self.account_type,
            "school_id": self.school_id
        }

class Model:
    def __init__(self):
        self.BASE_URL = "http://127.0.0.1:8000"
        self.supervisor_domain = 'example.com'


    def get_user_by_username(self, email):
        response = requests.get(f"{self.BASE_URL}/users/{email}")
        user = response.json()
        if 'email' in user:
            return User(user['email'], user['password'], user['account_type'], user['school_id'])
        else:
            print("Response JSON:", user)  # Debugging information
            return None

    def create_user(self, email, password, account_type, school_id):
        password_hash = generate_password_hash(password)
        user = User(email, password_hash, account_type, school_id)
        requests.post(f"{self.BASE_URL}/users/", json=user.to_dict())

    def create_school(self, name, address, city, county, postcode, phone, website, domain):
        school_data = School(name, address, city, county, postcode, phone, website, domain)
        requests.post(f"{self.BASE_URL}/schools/", json=school_data.to_dict())

    def get_domains(self):
        response = requests.get(f"{self.BASE_URL}/schools/")
        schools = response.json()
        domains = [{'id': school['id'], 'domain': school['domain']} for school in schools if 'domain' in school]
        return domains

    def add_contact(self, name, email, message):
        contact_data = {
            "name": name,
            "email": email,
            "message": message
        }
        requests.post(f"{self.BASE_URL}/contact/", json=contact_data)

    def get_contacts(self):
        response = requests.get(f"{self.BASE_URL}/contact/")
        return response.json()

    def delete_contact(self, id):
        response = requests.delete(f"{self.BASE_URL}/contact/{id}")
        return response.status_code == 204

    def get_sessions_by_username(self, email):
        response = requests.get(f"{self.BASE_URL}/sessions/{email}")
        return response.json()

    def get_sessions_by_school(self, school_id):
        response = requests.get(f"{self.BASE_URL}/sessions/school/{school_id}")
        return response.json()

    def get_sessions(self):
        response = requests.get(f"{self.BASE_URL}/sessions/")
        return response.json()

    def create_session(self, session_data):
        # If client is education type, get and add school info
        if 'client_id' in session_data:
            client_id = session_data['client_id']
            # Get client info to check account type
            response = requests.get(f"{self.BASE_URL}/users/{client_id}")

            # Check if the client exists
            if response.status_code == 404:
                print(f"Client ID {client_id} not found. Creating session without school info.")
            else:
                client = response.json()
                if client.get('account_type') == 'education' and client.get('school_id'):
                    # Add school_id to session data
                    session_data['school_id'] = client['school_id']

        # Create the session with whatever data we have
        response = requests.post(f"{self.BASE_URL}/sessions/", json=session_data)
        return response.json()

    def update_session(self, session_id, session_data):
        response = requests.put(f"{self.BASE_URL}/sessions/{session_id}", json=session_data)
        return response.json()

    def delete_session(self, session_id):
        response = requests.delete(f"{self.BASE_URL}/sessions/{session_id}")
        return response.status_code == 204

    def get_session(self, session_id):
        response = requests.get(f"{self.BASE_URL}/sessions/{session_id}")
        return response.json()

    def get_supervisors(self):
        response = requests.get(f"{self.BASE_URL}/users")
        users = response.json()
        supervisors = [user for user in users if user['account_type'] == 'supervisor']
        return supervisors

    def get_clients(self):
        response = requests.get(f"{self.BASE_URL}/users")
        users = response.json()
        clients = [user for user in users if user['account_type'] in ['education', 'other']]
        return clients

    def delete_user(self, user_id):
        response = requests.delete(f"{self.BASE_URL}/users/{user_id}")
        return response.status_code == 204


    def get_all_users(self):
        response = requests.get(f"{self.BASE_URL}/users")
        return response.json()

    def get_all_requests(self):
        response = requests.get(f"{self.BASE_URL}/session_edits")
        return response.json()

    def get_supervisor_requests(self, supervisor_id):
        response = requests.get(f"{self.BASE_URL}/session_edits/supervisor/{supervisor_id}")
        return response.json()

    def get_school_requests(self, school_id):
        response = requests.get(f"{self.BASE_URL}/session_edits/school/{school_id}")
        return response.json()

    def get_client_requests(self, client_id):
        response = requests.get(f"{self.BASE_URL}/session_edits/client/{client_id}")
        return response.json()

    def delete_request(self, request_id):
        response = requests.delete(f"{self.BASE_URL}/session_edits/{request_id}")
        return response.status_code == 204

    def get_school(self, school_id):
        response = requests.get(f"{self.BASE_URL}/schools/{school_id}")
        return response.json()

    def delete_school(self, school_id):
        response = requests.delete(f"{self.BASE_URL}/schools/{school_id}")
        return response.status_code == 204

    def update_school(self, school_id, school_data):
        response = requests.put(f"{self.BASE_URL}/schools/{school_id}", json=school_data)
        return response.json()

    def get_schools(self):
        response = requests.get(f"{self.BASE_URL}/schools/")
        return response.json()