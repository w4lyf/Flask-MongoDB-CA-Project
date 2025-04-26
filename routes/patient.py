from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bson.objectid import ObjectId
from datetime import datetime
from utils.decorators import role_required

patient = Blueprint('patient', __name__)

@patient.route('/patient/dashboard')
@role_required(['patient'])
def patient_dashboard():
    from app import mongo
    
    patient_id = session.get('user_id')
    patient = mongo.db.patients.find_one({"user_id": ObjectId(patient_id)})
    
    # Get upcoming appointments
    upcoming_appointments = list(mongo.db.appointments.find({
        "patient_id": ObjectId(patient_id),
        "status": {"$in": ["pending", "scheduled"]}
    }).sort("appointment_date", 1).limit(5))
    
    # Get appointment counts
    total_appointments = mongo.db.appointments.count_documents({"patient_id": ObjectId(patient_id)})
    completed_appointments = mongo.db.appointments.count_documents({
        "patient_id": ObjectId(patient_id),
        "status": "completed"
    })
    
    # Get doctor information for each appointment
    for appointment in upcoming_appointments:
        doctor = mongo.db.doctors.find_one({"user_id": appointment["doctor_id"]})
        if doctor:
            appointment["doctor_name"] = doctor.get("name", "Unknown")
            appointment["doctor_specialization"] = doctor.get("specialization", "")
    
    return render_template('patients/dashboard.html',
                          patient=patient,
                          upcoming_appointments=upcoming_appointments,
                          total_appointments=total_appointments,
                          completed_appointments=completed_appointments)

@patient.route('/patient/book-appointment', methods=['GET', 'POST'])
@role_required(['patient'])
def book_appointment():
    from app import mongo
    
    doctors = list(mongo.db.doctors.find({}))
    
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        appointment_date = request.form.get('appointment_date')
        symptoms = request.form.get('symptoms')
        
        # Convert string date to datetime object
        try:
            appointment_datetime = datetime.strptime(appointment_date, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format', 'danger')
            return render_template('patients/book_appointment.html', doctors=doctors)
        
        # Create appointment
        new_appointment = {
            "patient_id": ObjectId(session.get('user_id')),
            "doctor_id": ObjectId(doctor_id),
            "appointment_date": appointment_datetime,
            "symptoms": symptoms,
            "status": "pending",  # pending, scheduled, completed, cancelled
            "diagnosis": "",
            "prescription": "",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        mongo.db.appointments.insert_one(new_appointment)
        
        flash('Appointment booked successfully', 'success')
        return redirect(url_for('patient.my_appointments'))
    
    return render_template('patients/book_appointment.html', doctors=doctors)

@patient.route('/patient/appointments')
@role_required(['patient'])
def my_appointments():
    from app import mongo
    
    patient_id = session.get('user_id')
    
    # Default filter for upcoming appointments
    filter_status = request.args.get('status', 'all')
    
    if filter_status == 'all':
        appointments = list(mongo.db.appointments.find({
            "patient_id": ObjectId(patient_id)
        }).sort("appointment_date", -1))
    else:
        appointments = list(mongo.db.appointments.find({
            "patient_id": ObjectId(patient_id),
            "status": filter_status
        }).sort("appointment_date", -1))
    
    # Get doctor information for each appointment
    for appointment in appointments:
        doctor = mongo.db.doctors.find_one({"user_id": appointment["doctor_id"]})
        if doctor:
            appointment["doctor_name"] = doctor.get("name", "Unknown")
            appointment["doctor_specialization"] = doctor.get("specialization", "")
    
    return render_template('patients/appointments.html', appointments=appointments, filter_status=filter_status)

@patient.route('/patient/appointment/<appointment_id>')
@role_required(['patient'])
def view_appointment(appointment_id):
    from app import mongo
    
    appointment = mongo.db.appointments.find_one({"_id": ObjectId(appointment_id)})
    
    if not appointment:
        flash('Appointment not found', 'danger')
        return redirect(url_for('patient.my_appointments'))
    
    # Check if this appointment belongs to the logged in patient
    if str(appointment["patient_id"]) != session.get('user_id'):
        flash('You do not have permission to view this appointment', 'danger')
        return redirect(url_for('patient.my_appointments'))
    
    doctor = mongo.db.doctors.find_one({"user_id": appointment["doctor_id"]})
    
    return render_template('patients/view_appointment.html', appointment=appointment, doctor=doctor)

@patient.route('/patient/appointment/cancel/<appointment_id>')
@role_required(['patient'])
def cancel_appointment(appointment_id):
    from app import mongo
    
    appointment = mongo.db.appointments.find_one({"_id": ObjectId(appointment_id)})
    
    if not appointment:
        flash('Appointment not found', 'danger')
        return redirect(url_for('patient.my_appointments'))
    
    # Check if this appointment belongs to the logged in patient
    if str(appointment["patient_id"]) != session.get('user_id'):
        flash('You do not have permission to cancel this appointment', 'danger')
        return redirect(url_for('patient.my_appointments'))
    
    # Check if appointment can be cancelled (only pending or scheduled)
    if appointment["status"] not in ["pending", "scheduled"]:
        flash('This appointment cannot be cancelled', 'danger')
        return redirect(url_for('patient.my_appointments'))
    
    # Update appointment status
    mongo.db.appointments.update_one(
        {"_id": ObjectId(appointment_id)},
        {"$set": {
            "status": "cancelled",
            "updated_at": datetime.now()
        }}
    )
    
    flash('Appointment cancelled successfully', 'success')
    return redirect(url_for('patient.my_appointments'))

@patient.route('/patient/profile', methods=['GET', 'POST'])
@role_required(['patient'])
def patient_profile():
    from app import mongo
    
    patient_id = session.get('user_id')
    patient = mongo.db.patients.find_one({"user_id": ObjectId(patient_id)})
    
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        date_of_birth = request.form.get('date_of_birth')
        medical_history = request.form.get('medical_history')
        
        # Update patient profile
        mongo.db.patients.update_one(
            {"user_id": ObjectId(patient_id)},
            {"$set": {
                "name": name,
                "phone": phone,
                "address": address,
                "date_of_birth": date_of_birth,
                "medical_history": medical_history,
                "updated_at": datetime.now()
            }}
        )
        
        flash('Profile updated successfully', 'success')
        return redirect(url_for('patient.patient_profile'))
    
    return render_template('patients/profile.html', patient=patient)