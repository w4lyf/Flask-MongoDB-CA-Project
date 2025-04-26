import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb+srv://abhinav:abhinav@abhinav.4n5gyus.mongodb.net/hospital_db?retryWrites=true&w=majority&appName=abhinav'
    
    # Default admin credentials (for initial setup)
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'  # In production, use environment variables
    ADMIN_EMAIL = 'admin@hospital.com'