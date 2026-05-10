from flask import Blueprint, request, jsonify, render_template,redirect,url_for
from flask_login import login_required, current_user
from extensions import db 
from models import Attendance, Course, CourseEnrollment, User
from datetime import datetime, timedelta
from sqlalchemy import and_, desc

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')

@attendance_bp.route('/check-in', methods=['POST'])
@login_required
def check_in():
    """Check in for attendance"""
    try:
        data = request.get_json()
        
        if not data.get('course_id'):
            return jsonify({'error': 'Course ID is required'}), 400
        
        course = Course.query.get(data['course_id'])
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        today = datetime.utcnow().date()
        existing = Attendance.query.filter(
            and_(
                Attendance.user_id == current_user.id,
                Attendance.course_id == data['course_id'],
                Attendance.date == today,
                Attendance.check_in_time.isnot(None)
            )
        ).first()
        
        if existing:
            return jsonify({'error': 'Already checked in today for this course'}), 409
        
        attendance = Attendance(
            user_id=current_user.id,
            course_id=data['course_id'],
            check_in_time=datetime.utcnow(),
            status='present',
            date=today
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        return jsonify({
            'message': 'Check-in successful',
            'attendance_id': attendance.id,
            'check_in_time': attendance.check_in_time.isoformat()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/mark', methods=['POST'])
@login_required
def mark_attendance():
    course = Course.query.first()   # get any course

    if not course:
        return "No course found. Please add a course first."

    record = Attendance(
        user_id=current_user.id,
        course_id=course.id,
        check_in_time=datetime.utcnow()
    )

    db.session.add(record)
    db.session.commit()

    return redirect(url_for('attendance.view_attendance'))

@attendance_bp.route('/check-out/<int:attendance_id>', methods=['POST'])
@login_required
def check_out(attendance_id):
    """Check out from attendance"""
    try:
        attendance = Attendance.query.get(attendance_id)
        
        if not attendance:
            return jsonify({'error': 'Attendance record not found'}), 404
        
        if attendance.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if attendance.check_out_time:
            return jsonify({'error': 'Already checked out'}), 409
        
        attendance.check_out_time = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Check-out successful',
            'check_out_time': attendance.check_out_time.isoformat()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@attendance_bp.route('/view')
@login_required
def view_attendance():
    records = Attendance.query.all()
    return render_template("attendance.html", records=records)

@attendance_bp.route('/records', methods=['GET'])
@login_required
def get_attendance_records():
    """Get attendance records for current user"""
    try:
        course_id = request.args.get('course_id', type=int)
        days = request.args.get('days', default=30, type=int)
        
        query = Attendance.query.filter_by(user_id=current_user.id)
        
        if course_id:
            query = query.filter_by(course_id=course_id)
        
        start_date = datetime.utcnow().date() - timedelta(days=days)
        query = query.filter(Attendance.date >= start_date)
        
        records = query.order_by(desc(Attendance.date)).all()
        
        return jsonify({
            'total': len(records),
            'records': [{
                'id': r.id,
                'course_id': r.course_id,
                'course_name': r.course.name,
                'date': r.date.isoformat(),
                'check_in_time': r.check_in_time.isoformat() if r.check_in_time else None,
                'check_out_time': r.check_out_time.isoformat() if r.check_out_time else None,
                'status': r.status,
                'notes': r.notes
            } for r in records]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/summary', methods=['GET'])
@login_required
def get_attendance_summary():
    """Get attendance summary for current user"""
    try:
        course_id = request.args.get('course_id', type=int)
        days = request.args.get('days', default=30, type=int)
        
        query = Attendance.query.filter_by(user_id=current_user.id)
        
        if course_id:
            query = query.filter_by(course_id=course_id)
        
        start_date = datetime.utcnow().date() - timedelta(days=days)
        query = query.filter(Attendance.date >= start_date)
        
        records = query.all()
        
        total = len(records)
        present = len([r for r in records if r.status == 'present'])
        absent = len([r for r in records if r.status == 'absent'])
        late = len([r for r in records if r.status == 'late'])
        excused = len([r for r in records if r.status == 'excused'])
        
        attendance_percentage = (present / total * 100) if total > 0 else 0
        
        return jsonify({
            'total_sessions': total,
            'present': present,
            'absent': absent,
            'late': late,
            'excused': excused,
            'attendance_percentage': round(attendance_percentage, 2)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@attendance_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_attendance(id):
    record = Attendance.query.get(id)

    if not record:
        return "Record not found", 404

    db.session.delete(record)
    db.session.commit()

    return redirect(url_for('attendance.view_attendance'))