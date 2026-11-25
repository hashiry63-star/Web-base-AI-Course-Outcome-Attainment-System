from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, teacher, student

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    plos = db.relationship('PLO', backref='program', lazy=True, cascade='all, delete-orphan')
    courses = db.relationship('Course', backref='program', lazy=True)

class PLO(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    plo_code = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(500), nullable=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    semester = db.Column(db.String(50), nullable=False)
    teacher = db.relationship('User', backref='courses')
    clos = db.relationship('CLO', backref='course', lazy=True, cascade='all, delete-orphan')
    timetable = db.relationship('Timetable', backref='course', lazy=True, cascade='all, delete-orphan')
    outline = db.relationship('Outline', backref='course', lazy=True, cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='course', lazy=True, cascade='all, delete-orphan')

class CLO(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    clo_code = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    assessments = db.relationship('Assessment', backref='clo', lazy=True, cascade='all, delete-orphan')
    plo_mappings = db.relationship('CLO_PLO', backref='clo', lazy=True, cascade='all, delete-orphan')

class CLO_PLO(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clo_id = db.Column(db.Integer, db.ForeignKey('clo.id'), nullable=False)
    plo_id = db.Column(db.Integer, db.ForeignKey('plo.id'), nullable=False)
    plo = db.relationship('PLO')

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clo_id = db.Column(db.Integer, db.ForeignKey('clo.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    max_marks = db.Column(db.Integer, nullable=False)
    threshold = db.Column(db.Integer, default=50)
    marks = db.relationship('Mark', backref='assessment', lazy=True, cascade='all, delete-orphan')

class Mark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    marks_obtained = db.Column(db.Float, nullable=False)
    student = db.relationship('User', foreign_keys=[student_id])

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    student = db.relationship('User', foreign_keys=[student_id])

class Timetable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    time_slot = db.Column(db.String(50), nullable=False)
    room = db.Column(db.String(50), nullable=False)

class Outline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(1000), nullable=False)