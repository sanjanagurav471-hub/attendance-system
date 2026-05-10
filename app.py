import os
from flask import Flask
from flask_login import LoginManager
from config import config
from dotenv import load_dotenv
from extensions import db 

load_dotenv()

login_manager = LoginManager()

def create_app(config_name=None):
    """Application factory function"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    with app.app_context():
        from models import User, Attendance, Course

        db.create_all()

        user = User.query.first()

        if user:
            existing_course = Course.query.first()
    
            if not existing_course:
                course = Course(
                   code="CS101",
                   name="Computer Science",
                   instructor_id=user.id
                )
                db.session.add(course)
                db.session.commit()
        
        
        from routes.auth import auth_bp
        from routes.attendance import attendance_bp
        from routes.dashboard import dashboard_bp
        from routes.admin import admin_bp
        from routes.api import api_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(attendance_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(api_bp)
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
        
        @app.route('/')
        def index():
            return {'message': 'Welcome to Attendance System API'}, 200
    
    return app

app = create_app()