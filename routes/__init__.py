from routes.main import main
from routes.auth import auth
from routes.admin import admin
from routes.doctor import doctor
from routes.patient import patient

def register_blueprints(app):
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(doctor)
    app.register_blueprint(patient)