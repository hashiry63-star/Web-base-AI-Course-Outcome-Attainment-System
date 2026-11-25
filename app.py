from flask import Flask, redirect, url_for
from flask_login import LoginManager
from models import db, User
from auth import auth_bp
from admin import admin_bp
from teacher import teacher_bp
from student import student_bp

app = Flask(__name__)
app.secret_key = 'usp-co-attainment-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usp_attainment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(teacher_bp, url_prefix='/teacher')
app.register_blueprint(student_bp, url_prefix='/student')

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

def seed_demo_data():
    if User.query.first():
        return

    from models import Program, PLO, Course, CLO, CLO_PLO, Assessment, Mark, Enrollment, Timetable, Outline

    # Admin
    admin = User(name='Admin USP', email='admin@usp.edu.pk', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)

    # Teachers
    teachers = []
    teacher_data = [
        ('Dr. Ahmed Khan', 'ahmed@usp.edu.pk'),
        ('Dr. Sara Malik', 'sara@usp.edu.pk'),
        ('Mr. Bilal Raza', 'bilal@usp.edu.pk'),
    ]
    for name, email in teacher_data:
        t = User(name=name, email=email, role='teacher')
        t.set_password('teacher123')
        db.session.add(t)
        teachers.append(t)

    # Students
    students = []
    student_data = [
        ('Ali Hassan', 'ali@student.usp.edu.pk'),
        ('Fatima Zahra', 'fatima@student.usp.edu.pk'),
        ('Umar Farooq', 'umar@student.usp.edu.pk'),
        ('Ayesha Siddiq', 'ayesha@student.usp.edu.pk'),
        ('Hassan Raza', 'hassan@student.usp.edu.pk'),
        ('Zainab Noor', 'zainab@student.usp.edu.pk'),
        ('Talha Mehmood', 'talha@student.usp.edu.pk'),
        ('Sana Tariq', 'sana@student.usp.edu.pk'),
        ('Hamza Ali', 'hamza@student.usp.edu.pk'),
        ('Maria Khan', 'maria@student.usp.edu.pk'),
    ]
    for name, email in student_data:
        s = User(name=name, email=email, role='student')
        s.set_password('student123')
        db.session.add(s)
        students.append(s)

    db.session.flush()

    # Programs
    bit = Program(name='Bachelor of Information Technology')
    bscs = Program(name='Bachelor of Computer Science')
    db.session.add_all([bit, bscs])
    db.session.flush()

    # PLOs for BIT
    bit_plos = [
        PLO(program_id=bit.id, plo_code='PLO1', description='Apply knowledge of computing to solve complex problems'),
        PLO(program_id=bit.id, plo_code='PLO2', description='Design and implement software systems effectively'),
        PLO(program_id=bit.id, plo_code='PLO3', description='Communicate effectively in professional environments'),
    ]
    db.session.add_all(bit_plos)

    # PLOs for BSCS
    bscs_plos = [
        PLO(program_id=bscs.id, plo_code='PLO1', description='Demonstrate theoretical foundations of computer science'),
        PLO(program_id=bscs.id, plo_code='PLO2', description='Apply algorithms and data structures to real problems'),
        PLO(program_id=bscs.id, plo_code='PLO3', description='Work effectively in team-based software projects'),
    ]
    db.session.add_all(bscs_plos)
    db.session.flush()

    # Courses
    courses_data = [
        ('Data Structures', 'CS-201', bit.id, teachers[0].id, 'Fall 2024'),
        ('Web Development', 'CS-301', bit.id, teachers[1].id, 'Fall 2024'),
        ('Database Systems', 'CS-302', bscs.id, teachers[2].id, 'Fall 2024'),
        ('Algorithms', 'CS-401', bscs.id, teachers[0].id, 'Fall 2024'),
    ]
    courses = []
    for name, code, prog_id, teacher_id, semester in courses_data:
        c = Course(name=name, code=code, program_id=prog_id, teacher_id=teacher_id, semester=semester)
        db.session.add(c)
        courses.append(c)
    db.session.flush()

    # Timetable
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
    times = ['08:00 - 09:30', '10:00 - 11:30', '12:00 - 01:30', '02:00 - 03:30']
    rooms = ['Room 101', 'Room 202', 'Lab 1', 'Room 305']
    for i, course in enumerate(courses):
        db.session.add(Timetable(course_id=course.id, day=days[i], time_slot=times[i], room=rooms[i]))

    # Outline (4 weeks per course)
    outline_topics = [
        [('Arrays and Linked Lists', 'Introduction to linear data structures'),
         ('Stacks and Queues', 'LIFO and FIFO data structures with applications'),
         ('Trees and Binary Search Trees', 'Hierarchical data structures and traversal'),
         ('Graphs and Shortest Path', 'Graph representations and Dijkstra algorithm')],
        [('HTML and CSS Basics', 'Web page structure and styling fundamentals'),
         ('JavaScript Essentials', 'Client-side scripting and DOM manipulation'),
         ('Flask Framework', 'Python-based web development with Flask'),
         ('Database Integration', 'Connecting web apps to SQL databases')],
        [('ER Diagrams', 'Entity relationship modeling and design'),
         ('SQL Fundamentals', 'SELECT, INSERT, UPDATE, DELETE operations'),
         ('Normalization', 'First, second, and third normal forms'),
         ('Transactions and ACID', 'Database reliability and consistency')],
        [('Sorting Algorithms', 'Bubble, merge, quick sort analysis'),
         ('Searching Algorithms', 'Linear and binary search complexity'),
         ('Dynamic Programming', 'Memoization and tabulation techniques'),
         ('Greedy Algorithms', 'Greedy approach and applications')],
    ]
    for i, course in enumerate(courses):
        for week, (topic, desc) in enumerate(outline_topics[i], 1):
            db.session.add(Outline(course_id=course.id, week_number=week, topic=topic, description=desc))

    # CLOs
    clo_descriptions = [
        [('CLO1', 'Implement and analyze linear data structures'),
         ('CLO2', 'Apply tree and graph algorithms to solve problems'),
         ('CLO3', 'Evaluate time and space complexity of data structures')],
        [('CLO1', 'Design and build responsive web pages'),
         ('CLO2', 'Develop server-side applications using Flask'),
         ('CLO3', 'Integrate databases with web applications')],
        [('CLO1', 'Design normalized database schemas'),
         ('CLO2', 'Write complex SQL queries for data retrieval'),
         ('CLO3', 'Apply transaction management principles')],
        [('CLO1', 'Analyze algorithm complexity using Big-O notation'),
         ('CLO2', 'Implement dynamic programming solutions'),
         ('CLO3', 'Apply greedy algorithms to optimization problems')],
    ]

    import random
    all_clos = []
    for i, course in enumerate(courses):
        for clo_code, clo_desc in clo_descriptions[i]:
            clo = CLO(course_id=course.id, clo_code=clo_code, description=clo_desc)
            db.session.add(clo)
            all_clos.append(clo)
    db.session.flush()

    # Map CLOs to PLOs
    bit_clos = all_clos[:6]
    bscs_clos = all_clos[6:]
    for i, clo in enumerate(bit_clos):
        plo = bit_plos[i % 3]
        db.session.add(CLO_PLO(clo_id=clo.id, plo_id=plo.id))
    for i, clo in enumerate(bscs_clos):
        plo = bscs_plos[i % 3]
        db.session.add(CLO_PLO(clo_id=clo.id, plo_id=plo.id))

    # Assessments
    all_assessments = []
    for clo in all_clos:
        a1 = Assessment(clo_id=clo.id, name='Mid-Term Exam', max_marks=50, threshold=50)
        a2 = Assessment(clo_id=clo.id, name='Final Exam', max_marks=100, threshold=50)
        db.session.add_all([a1, a2])
        all_assessments.extend([a1, a2])
    db.session.flush()

    # Enroll all students in all courses
    for student in students:
        for course in courses:
            db.session.add(Enrollment(student_id=student.id, course_id=course.id))

    # Marks - varied so some students pass, some at risk, some repeat
    mark_patterns = [
        [45, 90], [38, 75], [25, 50], [48, 95], [30, 60],
        [42, 85], [20, 45], [46, 88], [35, 70], [28, 55]
    ]
    for i, student in enumerate(students):
        for j, assessment in enumerate(all_assessments):
            base = mark_patterns[i][j % 2]
            variation = random.randint(-5, 5)
            marks = min(max(base + variation, 0), assessment.max_marks)
            db.session.add(Mark(
                assessment_id=assessment.id,
                student_id=student.id,
                marks_obtained=marks
            ))

    db.session.commit()
    print("Demo data seeded successfully!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_demo_data()
    app.run(debug=True)