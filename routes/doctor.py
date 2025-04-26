from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bson.objectid import ObjectId
from datetime import datetime
from utils.decorators import role_required

doctor = Blueprint('doctor', __name__)

@doctor.route('/doctor/dashboard')
@role_required(['doctor'])
def doctor_dashboard():
    from app import mongo

    doctor_id = session.get('user_id')
    doctor = mongo.db.doctors.find_one({"user_id": ObjectId(doctor_id)})

    # Get upcoming appointments
    upcoming_appointments = list(mongo.db.appointments.find({
        "doctor_id": ObjectId(doctor_id),
        "status": "scheduled"
    }).sort("appointment_date", 1).limit(5))

    # Add patient info to each appointment
    for appointment in upcoming_appointments:
        patient = mongo.db.patients.find_one({"user_id": appointment["patient_id"]})
        appointment["patient_name"] = patient.get("name", "Unknown") if patient else "Unknown"

    # Get appointment counts
    total_appointments = mongo.db.appointments.count_documents({"doctor_id": ObjectId(doctor_id)})
    pending_appointments = mongo.db.appointments.count_documents({
        "doctor_id": ObjectId(doctor_id),
        "status": "pending"
    })

    return render_template('doctors/dashboard.html',
                          doctor=doctor,
                          upcoming_appointments=upcoming_appointments,
                          total_appointments=total_appointments,
                          pending_appointments=pending_appointments)


@doctor.route('/doctor/appointments')
@role_required(['doctor'])
def doctor_appointments():
    from app import mongo
    
    doctor_id = session.get('user_id')
    
    # Default filter for upcoming appointments
    filter_status = request.args.get('status', 'all')
    
    if filter_status == 'all':
        appointments = list(mongo.db.appointments.find({
            "doctor_id": ObjectId(doctor_id)
        }).sort("appointment_date", 1))
    else:
        appointments = list(mongo.db.appointments.find({
            "doctor_id": ObjectId(doctor_id),
            "status": filter_status
        }).sort("appointment_date", 1))
    
    # Get patient information for each appointment
    for appointment in appointments:
        patient = mongo.db.patients.find_one({"user_id": appointment["patient_id"]})
        if patient:
            appointment["patient_name"] = patient.get("name", "Unknown")
    
    return render_template('doctors/appointments.html', appointments=appointments, filter_status=filter_status)

@doctor.route('/doctor/appointment/<appointment_id>', methods=['GET', 'POST'])
@role_required(['doctor'])
def appointment_details(appointment_id):
    from app import mongo
    
    appointment = mongo.db.appointments.find_one({"_id": ObjectId(appointment_id)})
    
    if not appointment:
        flash('Appointment not found', 'danger')
        return redirect(url_for('doctor.doctor_appointments'))
    
    # Check if this appointment belongs to the logged in doctor
    if str(appointment["doctor_id"]) != session.get('user_id'):
        flash('You do not have permission to view this appointment', 'danger')
        return redirect(url_for('doctor.doctor_appointments'))
    
    patient = mongo.db.patients.find_one({"user_id": appointment["patient_id"]})
    
    if request.method == 'POST':
        status = request.form.get('status')
        diagnosis = request.form.get('diagnosis')
        prescription = request.form.get('prescription')
        
        # Update appointment
        mongo.db.appointments.update_one(
            {"_id": ObjectId(appointment_id)},
            {"$set": {
                "status": status,
                "diagnosis": diagnosis,
                "prescription": prescription,
                "updated_at": datetime.now()
            }}
        )
        
        flash('Appointment updated successfully', 'success')
        return redirect(url_for('doctor.doctor_appointments'))
    
    return render_template('doctors/appointment_details.html', appointment=appointment, patient=patient)

