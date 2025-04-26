from functools import wraps
from flask import session, redirect, url_for, flash
from bson.objectid import ObjectId

def login_required(f):
    @wraps(f) # Keeps the original function's name when decorating
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page', 'danger')
                return redirect(url_for('auth.login'))
            
            from app import mongo
            user = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
            if not user or user['role'] not in roles:
                flash('You do not have permission to access this page', 'danger')
                return redirect(url_for('main.index'))  # Make sure this is main.index
            return f(*args, **kwargs)
        return decorated_function
    return decorator