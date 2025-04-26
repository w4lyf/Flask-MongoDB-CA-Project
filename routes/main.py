from flask import Blueprint, render_template, redirect, url_for, session
from utils.decorators import login_required

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    role = session.get('role')
    if role == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    elif role == 'doctor':
        return redirect(url_for('doctor.doctor_dashboard'))
    elif role == 'patient':
        return redirect(url_for('patient.patient_dashboard'))
    
    # Default fallback
    return redirect(url_for('main.index'))