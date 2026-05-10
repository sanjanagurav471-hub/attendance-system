from flask import Blueprint, jsonify, render_template
from flask_login import login_required, current_user
from sqlalchemy import and_, func
from extensions import db 
from models import User, Attendance, Course
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/data', methods=['GET'])
@login_required
def dashboard_data():
    """Get dashboard data for current user"""
    try:
        user = current_user
        today = datetime.utcnow().date()
        
        today_attendance = Attendance.query.filter(
            and_(
                Attendance.user_id == user.id,
                Attendance.date == today
            )
        ).all()
        
        week_ago = today - timedelta(days=7)
        week_attendance = Attendance.query.filter(
            and_(
                Attendance.user_id == user.id,
                Attendance.date >= week_ago
            )
        ).all()
        
        week_present = len([a for a in week_attendance if a.status == 'present'])
        week_total = len(week_attendance)
        attendance_rate = (week_present / week_total * 100) if week_total > 0 else 0
        
        enrolled_courses = user.courses
        
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            },
            'today': {
                'check_ins': len([a for a in today_attendance if a.check_in_time]),
                'check_outs': len([a for a in today_attendance if a.check_out_time])
            },
            'week': {
                'total_sessions': week_total,
                'present': week_present,
                'attendance_rate': round(attendance_rate, 2)
            },
            'courses': {
                'total': len(enrolled_courses),
                'courses': [{
                    'id': c.id,
                    'code': c.code,
                    'name': c.name
                } for c in enrolled_courses]
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
   
@dashboard_bp.route('/')
@login_required
def dashboard_page():
    return render_template("dashboard.html")