from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from models import db, Course, CLO, Assessment, Mark, Enrollment, Outline, User
from utils import calculate_clo_attainment, calculate_course_attainment
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

teacher_bp = Blueprint('teacher', __name__)

def teacher_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'teacher':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def generate_chart(data, title):
    fig, ax = plt.subplots(figsize=(10, 5))
    labels = [d['label'] for d in data]
    values = [d['value'] for d in data]
    colors = ['#10b981' if v >= 60 else '#f59e0b' if v >= 40 else '#ef4444' for v in values]
    bars = ax.bar(labels, values, color=colors, width=0.5)
    ax.set_ylim(0, 110)
    ax.set_ylabel('Attainment %', color='white')
    ax.set_title(title, color='white', pad=15)
    ax.tick_params(colors='white')
    ax.set_facecolor('#1a1d2e')
    fig.patch.set_facecolor('#1a1d2e')
    for spine in ax.spines.values():
        spine.set_edgecolor('rgba(255,255,255,0.1)')
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{val:.1f}%', ha='center', va='bottom', color='white', fontsize=11)
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode()

# ─── Dashboard ───────────────────────────────────────────────
@teacher_bp.route('/')
@login_required
@teacher_required
def dashboard():
    courses = Course.query.filter_by(teacher_id=current_user.id).all()
    course_data = []
    for course in courses:
        attainment = calculate_course_attainment(course)
        enrollments = Enrollment.query.filter_by(course_id=course.id).count()
        course_data.append({
            'course': course,
            'attainment': attainment,
            'students': enrollments
        })
    return render_template('teacher/dashboard.html', course_data=course_data)

# ─── Course Detail ───────────────────────────────────────────
@teacher_bp.route('/course/<int:course_id>')
@login_required
@teacher_required
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    students = [e.student for e in enrollments]
    clo_data = []
    for clo in course.clos:
        attainment = calculate_clo_attainment(clo)
        clo_data.append({'clo': clo, 'attainment': attainment})
    return render_template('teacher/course_detail.html',
        course=course, clo_data=clo_data, students=students)

# ─── Assessments ─────────────────────────────────────────────
@teacher_bp.route('/course/<int:course_id>/clo/<int:clo_id>/add_assessment', methods=['POST'])
@login_required
@teacher_required
def add_assessment(course_id, clo_id):
    db.session.add(Assessment(
        clo_id=clo_id,
        name=request.form.get('name'),
        max_marks=int(request.form.get('max_marks')),
        threshold=int(request.form.get('threshold', 50))
    ))
    db.session.commit()
    flash('Assessment added', 'success')
    return redirect(url_for('teacher.course_detail', course_id=course_id))

# ─── Marks ───────────────────────────────────────────────────
@teacher_bp.route('/assessment/<int:assessment_id>/marks', methods=['GET', 'POST'])
@login_required
@teacher_required
def marks(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    course = assessment.clo.course
    enrollments = Enrollment.query.filter_by(course_id=course.id).all()
    students = [e.student for e in enrollments]

    if request.method == 'POST':
        for student in students:
            marks_val = request.form.get(f'marks_{student.id}')
            if marks_val:
                existing = Mark.query.filter_by(
                    assessment_id=assessment_id,
                    student_id=student.id
                ).first()
                if existing:
                    existing.marks_obtained = float(marks_val)
                else:
                    db.session.add(Mark(
                        assessment_id=assessment_id,
                        student_id=student.id,
                        marks_obtained=float(marks_val)
                    ))
        db.session.commit()
        flash('Marks saved successfully', 'success')
        return redirect(url_for('teacher.course_detail', course_id=course.id))

    existing_marks = {m.student_id: m.marks_obtained for m in assessment.marks}
    return render_template('teacher/marks.html',
        assessment=assessment, students=students,
        existing_marks=existing_marks, course=course)

# ─── Outline ─────────────────────────────────────────────────
@teacher_bp.route('/course/<int:course_id>/outline')
@login_required
@teacher_required
def outline(course_id):
    course = Course.query.get_or_404(course_id)
    outlines = Outline.query.filter_by(course_id=course_id).order_by(Outline.week_number).all()
    return render_template('teacher/outline.html', course=course, outlines=outlines)

@teacher_bp.route('/course/<int:course_id>/outline/add', methods=['POST'])
@login_required
@teacher_required
def add_outline(course_id):
    db.session.add(Outline(
        course_id=course_id,
        week_number=int(request.form.get('week_number')),
        topic=request.form.get('topic'),
        description=request.form.get('description')
    ))
    db.session.commit()
    flash('Week added to outline', 'success')
    return redirect(url_for('teacher.outline', course_id=course_id))

@teacher_bp.route('/outline/delete/<int:id>', methods=['POST'])
@login_required
@teacher_required
def delete_outline(id):
    o = Outline.query.get_or_404(id)
    course_id = o.course_id
    db.session.delete(o)
    db.session.commit()
    flash('Week deleted', 'success')
    return redirect(url_for('teacher.outline', course_id=course_id))

# ─── Timetable ───────────────────────────────────────────────
@teacher_bp.route('/timetable')
@login_required
@teacher_required
def timetable():
    from models import Timetable
    courses = Course.query.filter_by(teacher_id=current_user.id).all()
    course_ids = [c.id for c in courses]
    slots = Timetable.query.filter(Timetable.course_id.in_(course_ids)).all()
    return render_template('teacher/timetable.html', slots=slots)

# ─── Report ──────────────────────────────────────────────────
@teacher_bp.route('/course/<int:course_id>/report')
@login_required
@teacher_required
def report(course_id):
    course = Course.query.get_or_404(course_id)
    clo_data = []
    chart_data = []
    for clo in course.clos:
        attainment = calculate_clo_attainment(clo)
        clo_data.append({'clo': clo, 'attainment': attainment})
        chart_data.append({'label': clo.clo_code, 'value': attainment['percentage']})
    chart_img = generate_chart(chart_data, f'{course.name} – CLO Attainment') if chart_data else None
    overall = calculate_course_attainment(course)
    return render_template('teacher/report.html',
        course=course, clo_data=clo_data,
        chart_img=chart_img, overall=overall)