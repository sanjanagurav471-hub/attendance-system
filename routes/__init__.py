"""
Routes Package
==============

This package contains all the route blueprints for the attendance system.

Blueprints:
-----------
- auth_bp: Authentication and user profile routes
- attendance_bp: Attendance tracking routes (check-in/check-out)
- admin_bp: Admin management routes
- api_bp: RESTful API endpoints
- dashboard_bp: Dashboard data endpoints
"""

from flask import Blueprint

# Import all blueprints
from routes.auth import auth_bp
from routes.attendance import attendance_bp
from routes.admin import admin_bp
from routes.api import api_bp
from routes.dashboard import dashboard_bp

__all__ = [
    'auth_bp',
    'attendance_bp',
    'admin_bp',
    'api_bp',
    'dashboard_bp'
]