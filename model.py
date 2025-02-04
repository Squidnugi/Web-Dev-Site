from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class UserModel:
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(100), nullable=False, unique=True)
        email = db.Column(db.String(100), nullable=False, unique=True)

        def __repr__(self):
            return f'<User {self.username}>'

    @staticmethod
    def get_all_users():
        return UserModel.User.query.all()

    @staticmethod
    def add_user(username, email):
        user = UserModel.User(username=username, email=email)
        db.session.add(user)
        db.session.commit()
