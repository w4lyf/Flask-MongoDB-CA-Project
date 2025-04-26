from flask import Flask
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash
from datetime import datetime
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
mongo = PyMongo(app)

# Import route registration function
from routes import register_blueprints

# Register all blueprints
register_blueprints(app)

# Create indexes for faster lookups
with app.app_context():
    mongo.db.users.create_index("username", unique=True)
    mongo.db.users.create_index("email", unique=True)

# Initialize admin user if it doesn't exist
with app.app_context():
    if not mongo.db.users.find_one({"role": "admin"}):
        mongo.db.users.insert_one({
            "username": Config.ADMIN_USERNAME,
            "password": generate_password_hash(Config.ADMIN_PASSWORD),
            "email": Config.ADMIN_EMAIL,
            "role": "admin",
            "created_at": datetime.now()
        })
        print("Admin user created")

if __name__ == '__main__':
    app.run(debug=True)