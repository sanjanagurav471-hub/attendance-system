import os
from flask import Flask,redirect,url_for, render_template
from flask_login import LoginManager
from config import config
from dotenv import load_dotenv
from extensions import db

load_dotenv()

login_manager = LoginManager()

def create_app(config_name=None):

    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():

        from models import User, Attendance, Course

        db.create_all()

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
            return redirect(url_for('auth.login'))

        return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)