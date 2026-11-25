from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, Program, PLO, Course, CLO, CLO_PLO, Assessment, Enrollment, Timetable, Outline
from utils import calculate_course_attainment, calculate_plo_attainment

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

# ─── Dashboard ───────────────────────────────────────────────
@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    teachers = User.query.filter_by(role='teacher').all()
    students = User.query.filter_by(role='student').all()
    programs = Program.query.all()
    courses = Course.query.all()
    return render_template('admin/dashboard.html',
        teachers=teachers, students=students,
        programs=programs, courses=courses)

# ─── Teachers ────────────────────────────────────────────────
@admin_bp.route('/teachers')
@login_required
@admin_required
def teachers():
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('admin/teachers.html', teachers=teachers)

@admin_bp.route('/teachers/add', methods=['POST'])
@login_required
@admin_required
def add_teacher():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    if User.query.filter_by(email=email).first():
        flash('Email already exists', 'error')
    else:
        t = User(name=name, email=email, role='teacher')
        t.set_password(password)
        db.session.add(t)
        db.session.commit()
        flash('Teacher added successfully', 'success')
    return redirect(url_for('admin.teachers'))

@admin_bp.route('/teachers/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_teacher(id):
    t = User.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    flash('Teacher deleted', 'success')
    return redirect(url_for('admin.teachers'))

# ─── Students ────────────────────────────────────────────────
@admin_bp.route('/students')
@login_required
@admin_required
def students():
    students = User.query.filter_by(role='student').all()
    courses = Course.query.all()
    return render_template('admin/students.html', students=students, courses=courses)

@admin_bp.route('/students/add', methods=['POST'])
@login_required
@admin_required
def add_student():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    if User.query.filter_by(email=email).first():
        flash('Email already exists', 'error')
    else:
        s = User(name=name, email=email, role='student')
        s.set_password(password)
        db.session.add(s)
        db.session.commit()
        flash('Student added successfully', 'success')
    return redirect(url_for('admin.students'))

@admin_bp.route('/students/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_student(id):
    s = User.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    flash('Student deleted', 'success')
    return redirect(url_for('admin.students'))

@admin_bp.route('/students/enroll', methods=['POST'])
@login_required
@admin_required
def enroll_student():
    student_id = request.form.get('student_id')
    course_id = request.form.get('course_id')
    existing = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if existing:
        flash('Student already enrolled in this course', 'error')
    else:
        db.session.add(Enrollment(student_id=student_id, course_id=course_id))
        db.session.commit()
        flash('Student enrolled successfully', 'success')
    return redirect(url_for('admin.students'))

# ─── Programs & PLOs ─────────────────────────────────────────
@admin_bp.route('/programs')
@login_required
@admin_required
def programs():
    programs = Program.query.all()
    return render_template('admin/programs.html', programs=programs)

@admin_bp.route('/programs/add', methods=['POST'])
@login_required
@admin_required
def add_program():
    name = request.form.get('name')
    db.session.add(Program(name=name))
    db.session.commit()
    flash('Program added', 'success')
    return redirect(url_for('admin.programs'))

@admin_bp.route('/programs/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_program(id):
    p = Program.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    flash('Program deleted', 'success')
    return redirect(url_for('admin.programs'))

@admin_bp.route('/programs/<int:program_id>/plo/add', methods=['POST'])
@login_required
@admin_required
def add_plo(program_id):
    plo_code = request.form.get('plo_code')
    description = request.form.get('description')
    db.session.add(PLO(program_id=program_id, plo_code=plo_code, description=description))
    db.session.commit()
    flash('PLO added', 'success')
    return redirect(url_for('admin.programs'))

@admin_bp.route('/plo/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_plo(id):
    plo = PLO.query.get_or_404(id)
    db.session.delete(plo)
    db.session.commit()
    flash('PLO deleted', 'success')
    return redirect(url_for('admin.programs'))

# ─── Courses ─────────────────────────────────────────────────
@admin_bp.route('/courses')
@login_required
@admin_required
def courses():
    courses = Course.query.all()
    programs = Program.query.all()
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('admin/courses.html',
        courses=courses, programs=programs, teachers=teachers)

@admin_bp.route('/courses/add', methods=['POST'])
@login_required
@admin_required
def add_course():
    db.session.add(Course(
        name=request.form.get('name'),
        code=request.form.get('code'),
        program_id=request.form.get('program_id'),
        teacher_id=request.form.get('teacher_id'),
        semester=request.form.get('semester')
    ))
    db.session.commit()
    flash('Course added', 'success')
    return redirect(url_for('admin.courses'))

@admin_bp.route('/courses/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_course(id):
    c = Course.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    flash('Course deleted', 'success')
    return redirect(url_for('admin.courses'))

@admin_bp.route('/courses/<int:course_id>/clo/add', methods=['POST'])
@login_required
@admin_required
def add_clo(course_id):
    clo_code = request.form.get('clo_code')
    description = request.form.get('description')
    plo_id = request.form.get('plo_id')
    clo = CLO(course_id=course_id, clo_code=clo_code, description=description)
    db.session.add(clo)
    db.session.flush()
    if plo_id:
        db.session.add(CLO_PLO(clo_id=clo.id, plo_id=plo_id))
    db.session.commit()
    flash('CLO added', 'success')
    return redirect(url_for('admin.courses'))

# ─── Timetable ───────────────────────────────────────────────
@admin_bp.route('/timetable')
@login_required
@admin_required
def timetable():
    timetables = Timetable.query.all()
    courses = Course.query.all()
    return render_template('admin/timetable.html', timetables=timetables, courses=courses)

@admin_bp.route('/timetable/add', methods=['POST'])
@login_required
@admin_required
def add_timetable():
    db.session.add(Timetable(
        course_id=request.form.get('course_id'),
        day=request.form.get('day'),
        time_slot=request.form.get('time_slot'),
        room=request.form.get('room')
    ))
    db.session.commit()
    flash('Timetable slot added', 'success')
    return redirect(url_for('admin.timetable'))

@admin_bp.route('/timetable/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_timetable(id):
    t = Timetable.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    flash('Timetable slot deleted', 'success')
    return redirect(url_for('admin.timetable'))

# ─── System Report ───────────────────────────────────────────
@admin_bp.route('/report')
@login_required
@admin_required
def report():
    programs = Program.query.all()
    report_data = []
    for program in programs:
        plo_data = calculate_plo_attainment(program)
        course_data = []
        for course in program.courses:
            attainment = calculate_course_attainment(course)
            course_data.append({'course': course, 'attainment': attainment})
        report_data.append({
            'program': program,
            'plo_data': plo_data,
            'courses': course_data
        })
    return render_template('admin/report.html', report_data=report_data)