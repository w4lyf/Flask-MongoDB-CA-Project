from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    from app import mongo
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = mongo.db.users.find_one({"username": username})
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['role'] = user['role']
            
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    from app import mongo
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/register.html')
        
        if mongo.db.users.find_one({"username": username}):
            flash('Username already exists', 'danger')
            return render_template('auth/register.html')
        
        if mongo.db.users.find_one({"email": email}):
            flash('Email already exists', 'danger')
            return render_template('auth/register.html')
        
        # Only allow patient registration through this form (doctors are added by admin)
        if role not in ['patient']:
            flash('Invalid role selected', 'danger')
            return render_template('auth/register.html')
        
        # Create new user
        new_user = {
            "username": username,
            "email": email,
            "password": generate_password_hash(password),
            "role": role,
            "created_at": datetime.now()
        }
        
        user_id = mongo.db.users.insert_one(new_user).inserted_id
        
        # Create patient profile
        if role == 'patient':
            mongo.db.patients.insert_one({
                "user_id": user_id,
                "name": username,
                "email": email,
                "phone": "",
                "address": "",
                "date_of_birth": "",
                "medical_history": "",
                "created_at": datetime.now()
            })
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('main.index'))