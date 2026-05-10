from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db 
from models import User, Course, Attendance, CourseEnrollment
from datetime import datetime
from functools import wraps
from sqlalchemy import desc

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def get_all_users():
    """Get all users (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role = request.args.get('role', type=str)
        
        query = User.query
        if role:
            query = query.filter_by(role=role)
        
        pagination = query.paginate(page=page, per_page=per_page)
        
        return jsonify({
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'users': [{
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'role': u.role,
                'is_active': u.is_active,
                'created_at': u.created_at.isoformat()
            } for u in pagination.items]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@admin_required
def update_user(user_id):
    """Update user details (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if 'role' in data:
            if data['role'] not in ['student', 'teacher', 'admin']:
                return jsonify({'error': 'Invalid role'}), 400
            user.role = data['role']
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        if 'first_name' in data:
            user.first_name = data['first_name']
        
        if 'last_name' in data:
            user.last_name = data['last_name']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'User updated successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/courses', methods=['POST'])
@login_required
@admin_required
def create_course():
    """Create a new course (admin only)"""
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['code', 'name', 'instructor_id']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if Course.query.filter_by(code=data['code']).first():
            return jsonify({'error': 'Course code already exists'}), 409
        
        instructor = User.query.get(data['instructor_id'])
        if not instructor:
            return jsonify({'error': 'Instructor not found'}), 404
        
        course = Course(
            code=data['code'],
            name=data['name'],
            description=data.get('description', ''),
            instructor_id=data['instructor_id']
        )
        
        db.session.add(course)
        db.session.commit()
        
        return jsonify({
            'message': 'Course created successfully',
            'course_id': course.id,
            'code': course.code
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/courses', methods=['GET'])
@login_required
@admin_required
def get_all_courses():
    """Get all courses (admin only)"""
    try:
        courses = Course.query.all()
        
        return jsonify({
            'total': len(courses),
            'courses': [{
                'id': c.id,
                'code': c.code,
                'name': c.name,
                'instructor_id': c.instructor_id,
                'instructor_name': f"{c.instructor.first_name} {c.instructor.last_name}",
                'created_at': c.created_at.isoformat()
            } for c in courses]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/courses/<int:course_id>/students', methods=['POST'])
@login_required
@admin_required
def enroll_student(course_id):
    """Enroll student in course (admin only)"""
    try:
        data = request.get_json()
        
        if not data.get('student_id'):
            return jsonify({'error': 'Student ID is required'}), 400
        
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        student = User.query.get(data['student_id'])
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        existing = CourseEnrollment.query.filter_by(
            student_id=data['student_id'],
            course_id=course_id
        ).first()
        
        if existing:
            return jsonify({'error': 'Student already enrolled in this course'}), 409
        
        enrollment = CourseEnrollment(
            student_id=data['student_id'],
            course_id=course_id
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        return jsonify({'message': 'Student enrolled successfully'}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/attendance/report', methods=['GET'])
@login_required
@admin_required
def get_attendance_report():
    """Get attendance report for all users (admin only)"""
    try:
        course_id = request.args.get('course_id', type=int)
        
        query = Attendance.query
        if course_id:
            query = query.filter_by(course_id=course_id)
        
        records = query.order_by(desc(Attendance.date)).all()
        
        return jsonify({
            'total_records': len(records),
            'records': [{
                'id': r.id,
                'user_id': r.user_id,
                'username': r.user.username,
                'course_id': r.course_id,
                'course_code': r.course.code,
                'date': r.date.isoformat(),
                'check_in_time': r.check_in_time.isoformat() if r.check_in_time else None,
                'check_out_time': r.check_out_time.isoformat() if r.check_out_time else None,
                'status': r.status,
                'notes': r.notes
            } for r in records]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500