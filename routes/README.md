# Cloud-Based Attendance System

A comprehensive Flask-based attendance management system with SQLite database support. Built for tracking student/employee attendance with features for check-in/check-out, reporting, and admin management.

## Features

### User Management
- User registration and authentication
- Role-based access control (Student, Teacher, Admin)
- User profile management
- Account activation/deactivation

### Attendance Tracking
- Check-in/Check-out functionality
- Real-time attendance records
- Attendance status tracking (Present, Absent, Late, Excused)
- Historical attendance records

### Course Management
- Create and manage courses
- Enroll students in courses
- Track attendance per course
- Instructor assignment

### Admin Dashboard
- User management
- Course management
- Attendance reporting
- System statistics

### API Endpoints
- RESTful API for all operations
- JSON request/response format
- Comprehensive error handling

## Tech Stack

- **Backend**: Flask 2.3.3
- **Database**: SQLite
- **Authentication**: Flask-Login
- **ORM**: SQLAlchemy
- **Server**: Gunicorn
- **Cloud Ready**: Compatible with Google Cloud Platform

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/sanjanagurav471-hub/attendance-system.git
   cd attendance-system