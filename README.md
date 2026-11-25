# Web-Based AI Course Outcome Attainment System

A multi-role, intranet-ready web application that automates Outcome-Based Education (OBE) attainment tracking for universities. Teachers enter marks, and the system calculates CLO and PLO attainment, classifies performance, generates reports with charts, and gives students a personal repeat-risk analysis.

**Built at the University of Southern Punjab, Multan, Pakistan.**

---

## About the Author

I am a final-year Bachelor of Science in Information Technology (BSIT) student at the **University of Southern Punjab, Multan**. I designed and built this entire project myself: the backend, database, frontend, attainment and classification logic, and the intranet deployment setup. My project partner, **Muhammad Hamza**, handled the paperwork and documentation, including the SRS and the project report.

| | |
|---|---|
| **Developer** | Muhammad Hashir, BSIT-2Y-023R24P-3 |
| **Documentation** | Muhammad Hamza, BS-2Y-023R24-1 |
| **Supervisor** | Ma'am Hadia Rehan |
| **Institution** | University of Southern Punjab, Multan |
| **Program** | BSIT, 2024-2026 |

---

## The Problem

Universities following the HEC Pakistan OBE framework must measure, every semester, how well students achieve each Course Learning Outcome (CLO). Most departments do this by hand in Excel:

- It takes 3-4 hours per course.
- Spreadsheet formulas break silently and nobody notices.
- Every teacher uses a different template, so results cannot be compared across courses.
- Students never see which outcomes they are weak in until it is too late.

## The Solution

This system automates the whole cycle: institutional setup, marks entry, attainment calculation, classification, recommendations, and reporting. It runs on one machine and can be shared across a university lab network (intranet) with no internet connection and no paid software.

---

## Features

### Admin
- Create and delete teacher and student accounts
- Create programs (e.g. BIT, BSCS) and define their Program Learning Outcomes (PLOs)
- Create courses and assign them to teachers and programs
- Define CLOs per course and map each CLO to a PLO
- Enroll students in courses
- Manage the class timetable (day, time slot, room)
- View a system-wide PLO and course attainment report

### Teacher
- Sees only the courses assigned to them
- Views CLOs and their PLO mappings
- Adds assessments (mid-term, final, quiz, assignment) to each CLO with max marks and a pass threshold
- Enters marks for the whole class in a single form and can edit them later
- Manages a weekly course outline
- Views their personal timetable
- Generates a course report with a CLO table, a color-coded bar chart, and recommendations

### Student
- Sees all enrolled courses with attainment per course
- Sees marks per assessment and attainment per CLO
- Sees which PLO each CLO contributes to
- Views their personal timetable
- Gets a **Repeat Risk** page that classifies each subject as Clear, At Risk, or Repeat and shows exactly which CLOs are dragging the result down

---

## How It Works

### Data model

```
Program   -> PLO
Program   -> Course -> CLO -> Assessment -> Mark (one per student)
CLO       <-> PLO   (mapping table)
Student   <-> Course (enrollment)
Course    -> Timetable, Outline
```

Deleting a parent record cascades down, so the database never holds orphaned rows.

### Attainment calculation

For each CLO, the system collects student marks across all its assessments, converts them to percentages, and checks each against the assessment threshold (default 50%):

```
Attainment % = (students at or above threshold / total students) x 100
```

### Classification

| Attainment | Level |
|---|---|
| 80% and above | Excellent |
| 60% - 79% | Good |
| 40% - 59% | Average |
| Below 40% | Poor |

### PLO aggregation

PLO attainment is the average attainment of every CLO mapped to that PLO across the program's courses. This gives a program-level view of outcome achievement, which is the evidence accreditation bodies ask for.

### Recommendations

Every CLO below 60% is flagged in the teacher's report with a suggested intervention (extra tutorials, revision sessions, curriculum review). If every CLO is at 60% or above, the report confirms the current teaching approach is working.

### Student repeat risk

Each student's average attainment across a course's CLOs decides their status:

| Average attainment | Status |
|---|---|
| 50% and above | Clear |
| 40% - 49% | At Risk |
| Below 40% | Repeat |

Each CLO also gets an action hint: immediate attention required, additional practice needed, or keep it up.

### About the "AI"

The AI components are **rule-based** (threshold rules and IF-THEN logic), not machine learning. That is a deliberate choice: HEC's classification criteria are explicitly defined, a first deployment has no training data, and every result stays explainable and auditable by a quality committee.

### Charts

Charts are generated server-side with Matplotlib and embedded directly in the report page as base64 images, so reports are self-contained and print cleanly from the browser.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Web framework | Flask 3.0 (Blueprints: auth, admin, teacher, student) |
| Database | SQLite via SQLAlchemy 2.0 |
| Authentication | Flask-Login with Werkzeug password hashing |
| Frontend | HTML5, CSS3, Jinja2 templates |
| Charts | Matplotlib |

Everything is free and open source.

---

## Project Structure

```
USP_Attainment_System/
├── app.py             # App setup, Blueprint registration, demo data seeding
├── models.py          # SQLAlchemy database models
├── utils.py           # Attainment, classification, and PLO aggregation logic
├── auth.py            # Login and logout
├── admin.py           # Admin routes
├── teacher.py         # Teacher routes
├── student.py         # Student routes
├── requirements.txt   # Python dependencies
├── static/
└── templates/
    ├── base.html      # Shared layout and sidebar
    ├── auth/
    ├── admin/
    ├── teacher/
    └── student/
```

---

## Installation and Running

**Requirements:** Python 3.12 or newer and pip.

Download or clone this repository, open a terminal in the project folder, then run:

```bash
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in your browser. On first run the database is created and filled with demo data automatically.

### Demo accounts

| Role | Email | Password |
|---|---|---|
| Admin | admin@usp.edu.pk | admin123 |
| Teacher | ahmed@usp.edu.pk | teacher123 |
| Teacher | sara@usp.edu.pk | teacher123 |
| Teacher | bilal@usp.edu.pk | teacher123 |
| Student | ali@student.usp.edu.pk | student123 |
| Student | fatima@student.usp.edu.pk | student123 |

The demo data includes 1 admin, 3 teachers, 10 students, 2 programs, 4 courses, 3 CLOs per course, timetable slots, weekly outlines, and marks spread so that some students are Clear, some At Risk, and some flagged to Repeat.

> These are demo credentials only. Change them, and the `secret_key` in `app.py`, before any real deployment.

---

## Intranet Deployment (University Lab Network)

The app can serve a whole lab from one machine.

1. On the server machine, change the last line of `app.py` to:
   ```python
   app.run(host='0.0.0.0', port=5000, debug=False)
   ```
2. Find the server's IPv4 address with `ipconfig` (Windows).
3. Allow Python / port 5000 through Windows Firewall.
4. Run `python app.py`.
5. On any other computer on the same network, open `http://<server-ip>:5000`.

Client machines need nothing installed, only a browser. No internet is required after the initial setup.

---

## Testing

The system was verified with 30 manual functional test cases covering authentication, role-based access, CRUD for every module, marks entry and update, attainment and PLO calculation, chart generation, recommendations, repeat-risk classification, cascade deletion, printing, and access from a second machine over the LAN. Attainment results were also checked against manual calculation.

---

## Known Limitations

- SQLite handles concurrent writes poorly, so heavy simultaneous marks entry by many users is not recommended. Migrate to PostgreSQL for larger deployments.
- Marks are entered manually; there is no Excel or CSV import yet.
- There is no semester-to-semester history or trend analysis yet.
- The interface is built for desktop browsers and is not optimized for mobile.
- Flask's built-in server suits demos and small labs. Use a production server such as Waitress or Gunicorn for anything larger.

## Roadmap

- Excel/CSV bulk import of marks
- HOD and QEC officer roles
- Password reset and native PDF export
- Historical trend analysis across semesters
- PostgreSQL and production server deployment
- Predictive early-warning for at-risk students
- LMS integration (Moodle, Canvas)

---

## License

Released for academic and educational use. Developed as a Final Year Project at the University of Southern Punjab, Multan.

---

## Acknowledgements

Thanks to our supervisor, Ma'am Hadia Rehan, our Head of Department, Mr. Mubashir Malik, and the University of Southern Punjab for supporting this project.
