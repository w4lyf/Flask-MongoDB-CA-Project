from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash
from utils.decorators import role_required

admin = Blueprint('admin', __name__)

@admin.route('/admin/dashboard')
@role_required(['admin'])
def admin_dashboard():
    from app import mongo

    doctors_count = mongo.db.users.count_documents({"role": "doctor"})
    patients_count = mongo.db.users.count_documents({"role": "patient"})
    appointments_count = mongo.db.appointments.count_documents({})

    doctors = list(mongo.db.doctors.find())  # Fetch doctor profiles

    return render_template('admin/dashboard.html', 
                          doctors_count=doctors_count,
                          patients_count=patients_count,
                          appointments_count=appointments_count,
                          doctors=doctors)

@admin.route('/admin/doctors/add', methods=['GET', 'POST'])
@role_required(['admin'])
def add_doctor():
    from app import mongo
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        specialization = request.form.get('specialization')
        
        # Validation
        if mongo.db.users.find_one({"username": username}):
            flash('Username already exists', 'danger')
            return render_template('admin/add_doctor.html')
        
        if mongo.db.users.find_one({"email": email}):
            flash('Email already exists', 'danger')
            return render_template('admin/add_doctor.html')
        
        # Create new user with doctor role
        new_user = {
            "username": username,
            "email": email,
            "password": generate_password_hash(password),
            "role": "doctor",
            "created_at": datetime.now()
        }
        
        user_id = mongo.db.users.insert_one(new_user).inserted_id
        
        # Create doctor profile
        doctor_profile = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "specialization": specialization,
            "created_at": datetime.now()
        }
        
        mongo.db.doctors.insert_one(doctor_profile)
        
        flash('Doctor added successfully', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('admin/add_doctor.html')

@admin.route('/admin/doctors/delete/<doctor_id>', methods=['POST'])
@role_required(['admin'])
def delete_doctor(doctor_id):
    from app import mongo

    try:
        doctor = mongo.db.doctors.find_one({"_id": ObjectId(doctor_id)})
        if not doctor:
            flash("Doctor not found", "danger")
            return redirect(url_for('admin.admin_dashboard'))

        # Remove doctor profile
        mongo.db.doctors.delete_one({"_id": ObjectId(doctor_id)})

        # Remove user from users collection
        mongo.db.users.delete_one({"_id": doctor["user_id"]})

        flash("Doctor deleted successfully", "success")

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")

    return redirect(url_for('admin.admin_dashboard'))