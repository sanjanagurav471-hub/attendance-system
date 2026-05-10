from flask import Blueprint, jsonify
from extensions import db 
from models import User, Course, Attendance
from datetime import datetime, timedelta

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

@api_bp.route('/stats', methods=['GET'])
def get_statistics():
    """Get system statistics"""
    try:
        total_users = User.query.count()
        total_courses = Course.query.count()
        total_attendance = Attendance.query.count()
        
        week_ago = datetime.utcnow().date() - timedelta(days=7)
        recent_attendance = Attendance.query.filter(
            Attendance.date >= week_ago
        ).count()
        
        return jsonify({
            'total_users': total_users,
            'total_courses': total_courses,
            'total_attendance_records': total_attendance,
            'attendance_last_7_days': recent_attendance,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200