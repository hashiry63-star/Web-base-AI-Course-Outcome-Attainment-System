from flask import Blueprint, render_template, redirect, url_for
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from functools import wraps
from models import Course, Enrollment, Assessment, Mark
from utils import calculate_clo_attainment, calculate_course_attainment

student_bp = Blueprint('student', __name__)

def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'student':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

# ─── Dashboard ───────────────────────────────────────────────
@student_bp.route('/')
@login_required
def dashboard():
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    course_data = []
    for enrollment in enrollments:
        course = enrollment.course
        attainment = calculate_course_attainment(course, student_id=current_user.id)
        course_data.append({
            'course': course,
            'attainment': attainment
        })
    return render_template('student/dashboard.html', course_data=course_data)

# ─── Course Detail ───────────────────────────────────────────
@student_bp.route('/course/<int:course_id>')
@login_required
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    clo_data = []
    for clo in course.clos:
        attainment = calculate_clo_attainment(clo, student_id=current_user.id)
        assessment_marks = []
        for assessment in clo.assessments:
            mark = Mark.query.filter_by(
                assessment_id=assessment.id,
                student_id=current_user.id
            ).first()
            assessment_marks.append({
                'assessment': assessment,
                'mark': mark
            })
        clo_data.append({
            'clo': clo,
            'attainment': attainment,
            'assessment_marks': assessment_marks
        })
    return render_template('student/course_detail.html',
        course=course, clo_data=clo_data)

# ─── Timetable ───────────────────────────────────────────────
@student_bp.route('/timetable')
@login_required
def timetable():
    from models import Timetable
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    course_ids = [e.course_id for e in enrollments]
    slots = Timetable.query.filter(Timetable.course_id.in_(course_ids)).all()
    return render_template('student/timetable.html', slots=slots)

# ─── Repeat Risk ─────────────────────────────────────────────
@student_bp.route('/repeat-risk')
@login_required
def repeat_risk():
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    risk_data = []
    for enrollment in enrollments:
        course = enrollment.course
        attainment = calculate_course_attainment(course, student_id=current_user.id)
        clo_results = []
        for clo in course.clos:
            clo_att = calculate_clo_attainment(clo, student_id=current_user.id)
            clo_results.append({'clo': clo, 'attainment': clo_att})
        risk_data.append({
            'course': course,
            'attainment': attainment,
            'clo_results': clo_results
        })
    return render_template('student/repeat_risk.html', risk_data=risk_data)