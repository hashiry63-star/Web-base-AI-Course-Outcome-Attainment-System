def calculate_clo_attainment(clo, student_id=None):
    """Calculate attainment for a single CLO"""
    if not clo.assessments:
        return {'percentage': 0, 'level': 'No Data', 'passed': 0, 'total': 0}

    all_percentages = []

    for assessment in clo.assessments:
        if student_id:
            marks = [m for m in assessment.marks if m.student_id == student_id]
        else:
            marks = assessment.marks

        for mark in marks:
            pct = (mark.marks_obtained / assessment.max_marks) * 100
            all_percentages.append((pct, assessment.threshold))

    if not all_percentages:
        return {'percentage': 0, 'level': 'No Data', 'passed': 0, 'total': 0}

    if student_id:
        avg = sum(p for p, _ in all_percentages) / len(all_percentages)
        threshold = all_percentages[0][1]
        passed = 1 if avg >= threshold else 0
        total = 1
        percentage = avg
    else:
        total = len(set([m.student_id for a in clo.assessments for m in a.marks]))
        passed_students = set()
        all_students = set()

        for assessment in clo.assessments:
            for mark in assessment.marks:
                all_students.add(mark.student_id)
                pct = (mark.marks_obtained / assessment.max_marks) * 100
                if pct >= assessment.threshold:
                    passed_students.add(mark.student_id)

        total = len(all_students)
        passed = len(passed_students)
        percentage = (passed / total * 100) if total > 0 else 0

    if percentage >= 80:
        level = 'Excellent'
    elif percentage >= 60:
        level = 'Good'
    elif percentage >= 40:
        level = 'Average'
    else:
        level = 'Poor'

    return {
        'percentage': round(percentage, 2),
        'level': level,
        'passed': passed,
        'total': total
    }

def calculate_course_attainment(course, student_id=None):
    """Calculate overall attainment for a course"""
    if not course.clos:
        return {'percentage': 0, 'level': 'No Data'}

    clo_results = []
    for clo in course.clos:
        result = calculate_clo_attainment(clo, student_id)
        if result['level'] != 'No Data':
            clo_results.append(result['percentage'])

    if not clo_results:
        return {'percentage': 0, 'level': 'No Data'}

    avg = sum(clo_results) / len(clo_results)

    if avg >= 50:
        status = 'Clear'
    elif avg >= 40:
        status = 'At Risk'
    else:
        status = 'Repeat'

    if avg >= 80:
        level = 'Excellent'
    elif avg >= 60:
        level = 'Good'
    elif avg >= 40:
        level = 'Average'
    else:
        level = 'Poor'

    return {
        'percentage': round(avg, 2),
        'level': level,
        'status': status
    }

def calculate_plo_attainment(program, semester=None):
    """Calculate PLO attainment aggregated from CLOs"""
    plo_data = {}

    for plo in program.plos:
        plo_data[plo.id] = {
            'plo': plo,
            'percentages': [],
            'percentage': 0,
            'level': 'No Data'
        }

    for course in program.courses:
        if semester and course.semester != semester:
            continue
        for clo in course.clos:
            for mapping in clo.plo_mappings:
                if mapping.plo_id in plo_data:
                    result = calculate_clo_attainment(clo)
                    if result['level'] != 'No Data':
                        plo_data[mapping.plo_id]['percentages'].append(result['percentage'])

    for plo_id in plo_data:
        percentages = plo_data[plo_id]['percentages']
        if percentages:
            avg = sum(percentages) / len(percentages)
            plo_data[plo_id]['percentage'] = round(avg, 2)
            if avg >= 80:
                plo_data[plo_id]['level'] = 'Excellent'
            elif avg >= 60:
                plo_data[plo_id]['level'] = 'Good'
            elif avg >= 40:
                plo_data[plo_id]['level'] = 'Average'
            else:
                plo_data[plo_id]['level'] = 'Poor'

    return plo_data