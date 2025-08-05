from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    api_key = db.Column(db.String(120), nullable=False) # Assuming API key length, adjust if needed
    access_code = db.Column(db.String(120), nullable=False) # Assuming Access code length, adjust if needed

    def __repr__(self):
        return f'<User {self.email}>'

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            # Note: Returning api_key and access_code directly might be a security risk depending on usage.
            # Consider if these should be exposed via the API.
            'api_key': self.api_key,
            'access_code': self.access_code
        }

