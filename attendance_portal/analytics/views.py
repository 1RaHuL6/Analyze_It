from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Count
from .models import Student, Course,Enrollment, AttendanceSnapshot
from django.db.models.functions import TruncDate
from django.contrib.auth.decorators import login_required
from django.http import Http404
from collections import OrderedDict
import json

SNAPSHOT_LABELS = OrderedDict({
    "2017-09-25": "W1",
    "2017-10-16": "W2",
    "2017-11-06": "W3",
    "2017-11-27": "W4",
})

YEAR_DESCRIPTIONS = {
    0: 'Foundation Year',
    1: 'First Year',
    2: 'Second Year',
    3: 'Third Year (Final)',
    4: 'Fourth Year (Honors)',
    5: 'Fifth Year (Extended)',
    6: "PGT Year 1",
    7: "PGT Year 2",
}

@login_required
# level 1
def dashboard(request):
     ug_student_count = Student.objects.filter(level_of_study='UG').count()
     ug_course_count = Course.objects.filter( enrollment__student__level_of_study='UG').distinct().count()
     pg_student_count = Student.objects.filter(level_of_study='PGT').count()
     pg_course_count = Course.objects.filter(enrollment__student__level_of_study='PGT').distinct().count()
     
     week_labels = list(SNAPSHOT_LABELS.values())
     week_dates = list(SNAPSHOT_LABELS.keys())
     ug_weekly_attendance = []
     pgt_weekly_attendance = []
     ug_weekly_attendance_lt75 = []  
     pgt_weekly_attendance_lt75 = []  
     for date in week_dates:
         # UG
         ug_enrollments = Enrollment.objects.filter(student__level_of_study='UG')
         ug_enrollment_ids = ug_enrollments.values_list('id', flat=True)
         ug_snaps = AttendanceSnapshot.objects.filter(
             enrollment_id__in=ug_enrollment_ids,
             snapshot_date=date
         ).exclude(attendance_percent__isnull=True)
         ug_values = [s.attendance_percent for s in ug_snaps]
         ug_avg = round(sum(ug_values) / len(ug_values), 2) if ug_values else 0
         ug_weekly_attendance.append(ug_avg)
         
         ug_lt75_count = sum(1 for v in ug_values if v < 75)
         ug_total = len(ug_values)
         ug_lt75_pct = round((ug_lt75_count / ug_total) * 100, 2) if ug_total else 0
         ug_weekly_attendance_lt75.append(ug_lt75_pct)
         # PGT
         pgt_enrollments = Enrollment.objects.filter(student__level_of_study='PGT')
         pgt_enrollment_ids = pgt_enrollments.values_list('id', flat=True)
         pgt_snaps = AttendanceSnapshot.objects.filter(
             enrollment_id__in=pgt_enrollment_ids,
             snapshot_date=date
         ).exclude(attendance_percent__isnull=True)
         pgt_values = [s.attendance_percent for s in pgt_snaps]
         pgt_avg = round(sum(pgt_values) / len(pgt_values), 2) if pgt_values else 0
         pgt_weekly_attendance.append(pgt_avg)
         # PGT <75% percent
         pgt_lt75_count = sum(1 for v in pgt_values if v < 75)
         pgt_total = len(pgt_values)
         pgt_lt75_pct = round((pgt_lt75_count / pgt_total) * 100, 2) if pgt_total else 0
         pgt_weekly_attendance_lt75.append(pgt_lt75_pct)

     
     ug_attendance_nonzero = [v for v in ug_weekly_attendance if v > 0]
     avg_ug_attendance = round(sum(ug_attendance_nonzero) / len(ug_attendance_nonzero), 2) if ug_attendance_nonzero else 0
     pgt_attendance_nonzero = [v for v in pgt_weekly_attendance if v > 0]
     avg_pg_attendance = round(sum(pgt_attendance_nonzero) / len(pgt_attendance_nonzero), 2) if pgt_attendance_nonzero else 0
     
     low_attendance_ug_count = Enrollment.objects.filter(
        student__level_of_study='UG',
        total_attendance_percent__lt=75
    ).count()
      
     low_attendance_pg_count = Enrollment.objects.filter(
        student__level_of_study='PGT',
        total_attendance_percent__lt=75
    ).count()
     
     context = {
        'ug_student_count': ug_student_count,
        'ug_course_count': ug_course_count,
        'pg_student_count': pg_student_count,
        'pg_course_count': pg_course_count,
        'avg_ug_attendance': avg_ug_attendance,
        'avg_pg_attendance': avg_pg_attendance,
        'low_attendance_ug_count': low_attendance_ug_count,
        'low_attendance_pg_count': low_attendance_pg_count,
        'week_labels': week_labels,
        'ug_weekly_attendance': ug_weekly_attendance,
        'pgt_weekly_attendance': pgt_weekly_attendance,
        'ug_weekly_attendance_lt75': ug_weekly_attendance_lt75, 
        'pgt_weekly_attendance_lt75': pgt_weekly_attendance_lt75,  
    }
     return render(request, 'analytics/dashboard.html', context)

def get_status(avg_attendance):
    if avg_attendance >= 85:
        return "Excellent"
    elif 75 <= avg_attendance < 85:
        return "Good"
    elif 65 <= avg_attendance < 75:
        return "Monitor"
    else:
        return "Critical"
        
def get_year_color(year):
    """Return RGB color string for each year"""
    colors = [
        '255, 99, 132',    # Year 0 - Red
        '54, 162, 235',     # Year 1 - Blue
        '255, 206, 86',     # Year 2 - Yellow
        '75, 192, 192',     # Year 3 - Teal
        '153, 102, 255',    # Year 4 - Purple
        '255, 159, 64'      # Year 5 - Orange
    ]
    return colors[year]    
    
@login_required
def ug_year_selection(request):
    year_data = []
    
    for year in range(6):  # 0 to 5 years, as number of years will remain same
        students = Student.objects.filter(level_of_study='UG', year_of_course=year)
        student_ids = students.values_list('id', flat=True)
        enrollments = Enrollment.objects.filter(student_id__in=student_ids)
        enrollment_ids = enrollments.values_list('id', flat=True)

        student_count = students.count()
        course_count = enrollments.values('course').distinct().count()

       
        attendance_values = enrollments.exclude(total_attendance_percent__isnull=True).values_list('total_attendance_percent', flat=True)
        avg_attendance = sum(attendance_values) / len(attendance_values) if attendance_values else 0
        low_attendance_count = enrollments.filter(total_attendance_percent__lt=75).count()

        
        weekly_attendance = {}
        weekly_values = {label: [] for label in SNAPSHOT_LABELS.values()}  
        
        snapshots = AttendanceSnapshot.objects.filter(
            enrollment_id__in=enrollment_ids,
            snapshot_date__in=SNAPSHOT_LABELS.keys()
        ).exclude(attendance_percent__isnull=True)
        
        
        for snap in snapshots:
            date_str = snap.snapshot_date.strftime("%Y-%m-%d")
            if date_str in SNAPSHOT_LABELS:
                week_label = SNAPSHOT_LABELS[date_str]
                weekly_values[week_label].append(snap.attendance_percent)
        
        
        for week_label, values in weekly_values.items():
            weekly_avg = round(sum(values) / len(values), 2) if values else 0
            weekly_attendance[week_label] = weekly_avg
            
    


        year_data.append({
            'year': year,
            'description': YEAR_DESCRIPTIONS.get(year, f"Year {year}"),
            'course_count': course_count,
            'student_count': student_count,
            'avg_attendance': round(avg_attendance, 2),
            'low_attendance_count': low_attendance_count,
            'status': get_status(avg_attendance),
            'weekly_attendance': weekly_attendance,
            'week_labels': list(SNAPSHOT_LABELS.values()),  
            'attendance_values': [weekly_attendance.get(label, 0) for label in SNAPSHOT_LABELS.values()],
        })
    
    
    years = [y['year'] for y in year_data]
    week_labels = list(SNAPSHOT_LABELS.values())

    
    week_to_year_attendance = {week: [] for week in week_labels}
    for week in week_labels:
        for y in year_data:
            week_to_year_attendance[week].append(y['weekly_attendance'].get(week, 0))

    radar_data = {
        'labels': years,  
        'datasets': []
    }
    for i, week in enumerate(week_labels):
        rgb = get_year_color(i)  
        dataset = {
            'label': week,
            'data': week_to_year_attendance[week],
            'borderColor': f"rgb({rgb})",
            'backgroundColor': f"rgba({rgb}, 0.2)",
            'pointBackgroundColor': f"rgb({rgb})",
            'pointRadius': 4,
            'borderWidth': 2
        }
        radar_data['datasets'].append(dataset)

    context = {
        'year_data': year_data,
        'radar_data': radar_data  
    }
    return render(request, 'analytics/ug_year_selection.html', context)
# level 2 UG    
@login_required
def ug_year_selection_1(request):
    year_data = []

    for year in range(6):  # 0 to 5 years, as number of years will remain same
        students = Student.objects.filter(level_of_study='UG', year_of_course=year)
        student_ids = students.values_list('id', flat=True)

        enrollments = Enrollment.objects.filter(student_id__in=student_ids)

        student_count = students.count()
        course_count = enrollments.values('course').distinct().count()

        
        attendance_values = enrollments.exclude(total_attendance_percent__isnull=True).values_list('total_attendance_percent', flat=True)
        avg_attendance = sum(attendance_values) / len(attendance_values) if attendance_values else 0

        # Count students with < 75% average attendance
        low_attendance_count = enrollments.filter(total_attendance_percent__lt=75).count()

        year_data.append({
            'year': year,
            'description': YEAR_DESCRIPTIONS.get(year, f"Year {year}"),
            'course_count': course_count,
            'student_count': student_count,
            'avg_attendance': round(avg_attendance, 2),
            'low_attendance_count': low_attendance_count,
            'status': get_status(avg_attendance),
        })
           
    
    context = {
        'year_data': year_data,
    }
    return render(request, 'analytics/ug_year_selection.html', context)
    
#level 2 PG
@login_required
def pg_year_selection(request):
    year_data = []

    for year in range(1, 3):  # 1 to 2 years
        students = Student.objects.filter(level_of_study='PGT', year_of_course=year)
        student_ids = students.values_list('id', flat=True)
        enrollments = Enrollment.objects.filter(student_id__in=student_ids)
        enrollment_ids = enrollments.values_list('id', flat=True)

        student_count = students.count()
        course_count = enrollments.values('course').distinct().count()

        # --- Weekly attendance calculation ---
        weekly_attendance = {}
        weekly_values = {label: [] for label in SNAPSHOT_LABELS.values()}
        snapshots = AttendanceSnapshot.objects.filter(
            enrollment_id__in=enrollment_ids,
            snapshot_date__in=SNAPSHOT_LABELS.keys()
        ).exclude(attendance_percent__isnull=True)
        for snap in snapshots:
            date_str = snap.snapshot_date.strftime("%Y-%m-%d")
            if date_str in SNAPSHOT_LABELS:
                week_label = SNAPSHOT_LABELS[date_str]
                weekly_values[week_label].append(snap.attendance_percent)
        for week_label, values in weekly_values.items():
            weekly_avg = round(sum(values) / len(values), 2) if values else 0
            weekly_attendance[week_label] = weekly_avg

        # --- Dynamically calculate avg_attendance as mean of 4 weeks ---
        week_attendance_values = [v for v in weekly_attendance.values() if v > 0]
        avg_attendance = round(sum(week_attendance_values) / len(week_attendance_values), 2) if week_attendance_values else 0

        # Count students with < 75% average attendance
        low_attendance_count = enrollments.filter(total_attendance_percent__lt=75).count()

        year_data.append({
            'year': year,
            'description': YEAR_DESCRIPTIONS.get(year, f"Year {year}"),
            'course_count': course_count,
            'student_count': student_count,
            'avg_attendance': avg_attendance,
            'low_attendance_count': low_attendance_count,
            'status': get_status(avg_attendance),
            'weekly_attendance': weekly_attendance,
            'week_labels': list(SNAPSHOT_LABELS.values()),
            'attendance_values': [weekly_attendance.get(label, 0) for label in SNAPSHOT_LABELS.values()],
        })

    
    week_labels = list(SNAPSHOT_LABELS.values())
    radar_data = {
        'labels': week_labels,  # weeks on axis
        'datasets': []
    }
    for y in year_data:
        rgb = get_year_color(y['year'])
        dataset = {
            'label': f"Year {y['year']}",
            'data': [y['weekly_attendance'].get(week, 0) for week in week_labels],
            'borderColor': f"rgb({rgb})",
            'backgroundColor': f"rgba({rgb}, 0.2)",
            'pointBackgroundColor': f"rgb({rgb})",
            'pointRadius': 4,
            'borderWidth': 2
        }
        radar_data['datasets'].append(dataset)

    context = {
        'year_data': year_data,
        'radar_data': radar_data
    }
    return render(request, 'analytics/pg_year_selection.html', context)

#level 3 UG
@login_required
def course_overview_by_year(request, year):
    year = int(year)

    # Fetch all courses for this UG year
    students = Student.objects.filter(level_of_study='UG', year_of_course=year)
    student_ids = students.values_list('id', flat=True)
    enrollments = Enrollment.objects.filter(student_id__in=student_ids)

    courses = Course.objects.filter(enrollment__student_id__in=student_ids).distinct()

    course_data = []
    for course in courses:
        course_enrollments = enrollments.filter(course=course)
        enrollment_ids = course_enrollments.values_list('id', flat=True)
        # Calculate weekly attendance for this course (4 weeks)
        weekly_attendance = []
        for date in SNAPSHOT_LABELS.keys():
            snaps = AttendanceSnapshot.objects.filter(
                enrollment_id__in=enrollment_ids,
                snapshot_date=date
            ).exclude(attendance_percent__isnull=True)
            values = [s.attendance_percent for s in snaps]
            avg = round(sum(values) / len(values), 2) if values else 0
            weekly_attendance.append(avg)
        # Calculate avg_attendance as mean of 4 weeks
        nonzero = [v for v in weekly_attendance if v > 0]
        avg_attendance = round(sum(nonzero) / len(nonzero), 2) if nonzero else 0
        low_attendance_count = course_enrollments.filter(total_attendance_percent__lt=75).count()
        student_count = course_enrollments.count()

        def get_status(avg):
            if avg >= 85:
                return 'Good'
            elif avg >= 75:
                return 'Monitor'
            else:
                return 'At Risk'

        course_data.append({
            'code': course.code,
            'title': course.title,
            'student_count': student_count,
            'avg_attendance': avg_attendance,
            'low_attendance_display': f"{low_attendance_count} ({round((low_attendance_count / student_count) * 100, 1)}%)" if student_count else "0",
            'status': get_status(avg_attendance),
            'weekly_attendance': weekly_attendance,  
        })
    course_data_sorted = sorted(course_data, key=lambda x: x['avg_attendance'])

    return render(request, "analytics/course_overview.html", {
        'year': year,
        'courses': course_data_sorted,
    })

# level 3 PG
@login_required
def course_overview_by_year_pg(request, year):
    year = int(year)

    # Fetch all courses for this PGT year
    students = Student.objects.filter(level_of_study='PGT', year_of_course=year)
    student_ids = students.values_list('id', flat=True)
    enrollments = Enrollment.objects.filter(student_id__in=student_ids)

    courses = Course.objects.filter(enrollment__student_id__in=student_ids).distinct()

    course_data = []
    for course in courses:
        course_enrollments = enrollments.filter(course=course)
        enrollment_ids = course_enrollments.values_list('id', flat=True)
        # Calculate weekly attendance for this course (4 weeks)
        weekly_attendance = []
        for date in SNAPSHOT_LABELS.keys():
            snaps = AttendanceSnapshot.objects.filter(
                enrollment_id__in=enrollment_ids,
                snapshot_date=date
            ).exclude(attendance_percent__isnull=True)
            values = [s.attendance_percent for s in snaps]
            avg = round(sum(values) / len(values), 2) if values else 0
            weekly_attendance.append(avg)
        # Calculate avg_attendance as mean of 4 weeks
        nonzero = [v for v in weekly_attendance if v > 0]
        avg_attendance = round(sum(nonzero) / len(nonzero), 2) if nonzero else 0
        low_attendance_count = course_enrollments.filter(total_attendance_percent__lt=75).count()
        student_count = course_enrollments.count()

        def get_status(avg):
            if avg >= 85:
                return 'Good'
            elif avg >= 75:
                return 'Monitor'
            else:
                return 'At Risk'

        course_data.append({
            'code': course.code,
            'title': course.title,
            'student_count': student_count,
            'avg_attendance': avg_attendance,
            'low_attendance_display': f"{low_attendance_count} ({round((low_attendance_count / student_count) * 100, 1)}%)" if student_count else "0",
            'status': get_status(avg_attendance),
            'weekly_attendance': weekly_attendance,  # 4 week values for timeline
        })
    course_data_sorted = sorted(course_data, key=lambda x: x['avg_attendance'])

    return render(request, "analytics/course_overview_pg.html", {
        'year': year,
        'courses': course_data_sorted,
    })

#level 4 UG
@login_required
def course_student_list(request, course_code, year):
    course = get_object_or_404(Course, code=course_code)
    
    enrollments = Enrollment.objects.filter(
        course__code=course_code,
        student__year_of_course=year
    ).select_related('student')
    
    student_data = []
    for e in enrollments:
        # Dynamically calculate average attendance from 4 weekly snapshots
        snapshots = AttendanceSnapshot.objects.filter(
            enrollment=e,
            snapshot_date__in=SNAPSHOT_LABELS.keys()
        ).exclude(attendance_percent__isnull=True).order_by('snapshot_date')
        snapshot_values = [s.attendance_percent for s in snapshots]
        if snapshot_values:
            avg_attendance = round(sum(snapshot_values) / len(snapshot_values), 2)
        else:
            avg_attendance = 'N/A'
        student_data.append({
            'user_id': e.student.user_id,
            'attendance': avg_attendance,
            'year': e.student.year_of_course  
        })
    student_data_sorted = sorted(student_data, key=lambda x: (x['attendance'] if x['attendance'] != 'N/A' else -1))
    
    back_url = request.META.get('HTTP_REFERER', '/')
    context = {
        'course': course,
        'students': student_data_sorted,
        'back_url': back_url,
        'year': year  
    }
    
    return render(request, 'analytics/course_students.html', context)

#level 4 PGT
@login_required
def course_student_list_pg(request, course_code, year):
    course = get_object_or_404(Course, code=course_code)
    # Filter enrollments by both course and student's year
    enrollments = Enrollment.objects.filter(
        course__code=course_code,
        student__year_of_course=year
    ).select_related('student')
    
    student_data = []
    for e in enrollments:
        
        snapshots = AttendanceSnapshot.objects.filter(
            enrollment=e,
            snapshot_date__in=SNAPSHOT_LABELS.keys()
        ).exclude(attendance_percent__isnull=True).order_by('snapshot_date')
        snapshot_values = [s.attendance_percent for s in snapshots]
        if snapshot_values:
            avg_attendance = round(sum(snapshot_values) / len(snapshot_values), 2)
        else:
            avg_attendance = 'N/A'
        student_data.append({
            'user_id': e.student.user_id,
            'attendance': avg_attendance,
            'year': e.student.year_of_course  
        })
    student_data_sorted = sorted(student_data, key=lambda x: (x['attendance'] if x['attendance'] != 'N/A' else -1))
    
    back_url = request.META.get('HTTP_REFERER', '/')
    context = {
        'course': course,
        'students': student_data_sorted,
        'back_url': back_url,
        'year': year  # Pass year to template
    }
    return render(request, 'analytics/course_students_pg.html', context)

#level 5 UG
@login_required   
def student_attendance_details(request, course_code, year, student_id):
    course = get_object_or_404(Course, code=course_code)
    student = get_object_or_404(Student, user_id=student_id, year_of_course=year)
    enrollment = get_object_or_404(Enrollment, course=course, student=student)

    # Calculate average attendance for all students in the given course, year, and level (UG)
    enrollments_in_course_year = Enrollment.objects.filter(
        student__level_of_study='UG',
        student__year_of_course=year,
        course=course
    )
    enrollment_ids = enrollments_in_course_year.values_list('id', flat=True)
    weekly_attendance = []
    for date in SNAPSHOT_LABELS.keys():
        snaps = AttendanceSnapshot.objects.filter(
            enrollment_id__in=enrollment_ids,
            snapshot_date=date
        ).exclude(attendance_percent__isnull=True)
        values = [s.attendance_percent for s in snaps]
        avg = round(sum(values) / len(values), 2) if values else 0
        weekly_attendance.append(avg)
    nonzero = [v for v in weekly_attendance if v > 0]
    course_average = round(sum(nonzero) / len(nonzero), 2) if nonzero else 0

    # Get snapshots and map to week labels
    snapshots = AttendanceSnapshot.objects.filter(enrollment=enrollment).order_by('snapshot_date')

    week_labels = []
    attendance_values_list = []

    for snap in snapshots:
        label = SNAPSHOT_LABELS.get(snap.snapshot_date.strftime("%Y-%m-%d"))
        if label:
            week_labels.append(label)
            attendance_values_list.append(snap.attendance_percent or 0)
    
   
    student_attendance = 0
    if attendance_values_list:
        student_attendance = round(sum(attendance_values_list) / len(attendance_values_list), 2)
    
    attended_sessions = enrollment.total_attended or 0
    missed_sessions = enrollment.total_non_attended or 0
    difference = round(student_attendance - course_average, 2)

    context = {
        'course': course,
        'student': student,
        'enrollment': enrollment,
        'year': year,
        'student_attendance': student_attendance,  
        'course_average': course_average,
        'difference': difference,
        'attended_sessions': attended_sessions,
        'missed_sessions': missed_sessions,
        'snapshots': snapshots,
        'week_labels': week_labels,
        'attendance_values': attendance_values_list,
    }
    return render(request, 'analytics/student_detail.html', context)

#level 5 PGT
@login_required   
def student_attendance_details_pg(request, course_code, year, student_id):
    course = get_object_or_404(Course, code=course_code)
    student = get_object_or_404(Student, user_id=student_id, year_of_course=year)
    enrollment = get_object_or_404(Enrollment, course=course, student=student)

    # Calculate average attendance for all students in the given course, year, and level (PGT)
    enrollments_in_course_year = Enrollment.objects.filter(
        student__level_of_study='PGT',
        student__year_of_course=year,
        course=course
    )
    enrollment_ids = enrollments_in_course_year.values_list('id', flat=True)
    weekly_attendance = []
    for date in SNAPSHOT_LABELS.keys():
        snaps = AttendanceSnapshot.objects.filter(
            enrollment_id__in=enrollment_ids,
            snapshot_date=date
        ).exclude(attendance_percent__isnull=True)
        values = [s.attendance_percent for s in snaps]
        avg = round(sum(values) / len(values), 2) if values else 0
        weekly_attendance.append(avg)
    nonzero = [v for v in weekly_attendance if v > 0]
    course_average = round(sum(nonzero) / len(nonzero), 2) if nonzero else 0

    # Get snapshots and map to week labels
    snapshots = AttendanceSnapshot.objects.filter(enrollment=enrollment).order_by('snapshot_date')

    week_labels = []
    attendance_values_list = []

    for snap in snapshots:
        label = SNAPSHOT_LABELS.get(snap.snapshot_date.strftime("%Y-%m-%d"))
        if label:
            week_labels.append(label)
            attendance_values_list.append(snap.attendance_percent or 0)
    
    # Calculate dynamic student attendance as average of snapshot values
    student_attendance = 0
    if attendance_values_list:
        student_attendance = round(sum(attendance_values_list) / len(attendance_values_list), 2)
    
    attended_sessions = enrollment.total_attended or 0
    missed_sessions = enrollment.total_non_attended or 0
    difference = round(student_attendance - course_average, 2)

    context = {
        'course': course,
        'student': student,
        'enrollment': enrollment,
        'year': year,
        'student_attendance': student_attendance,  
        'course_average': course_average,
        'difference': difference,
        'attended_sessions': attended_sessions,
        'missed_sessions': missed_sessions,
        'snapshots': snapshots,
        'week_labels': week_labels,
        'attendance_values': attendance_values_list,
    }
    return render(request, 'analytics/student_detail_pg.html', context)

#search featre
@login_required
def search_view(request):
    query = request.GET.get('query', '').strip()
    search_type = request.GET.get('search_type', 'student')
    
    if not query:
        return render(request, 'analytics/search_results.html', {
            'error': 'Please enter a search term.',
            'query': '',
            'search_type': search_type
        })
    
    if search_type == 'student':
        try:
            student = Student.objects.get(user_id=query)
            
            enrollments = Enrollment.objects.filter(student=student).select_related('course')
            
            enrollment_data = []
            for enrollment in enrollments:
                snapshots = AttendanceSnapshot.objects.filter(
                    enrollment=enrollment
                ).exclude(attendance_percent__isnull=True).order_by('snapshot_date')
                
                attendance_values = [s.attendance_percent for s in snapshots]
                avg_attendance = round(sum(attendance_values) / len(attendance_values), 2) if attendance_values else 0
                
                week_labels = []
                attendance_values_list = []
                
                for snap in snapshots:
                    label = SNAPSHOT_LABELS.get(snap.snapshot_date.strftime("%Y-%m-%d"))
                    if label:
                        week_labels.append(label)
                        attendance_values_list.append(snap.attendance_percent or 0)
                
                enrollment_data.append({
                    'enrollment': enrollment,
                    'course': enrollment.course,
                    'avg_attendance': avg_attendance,
                    'week_labels': week_labels,
                    'attendance_values': attendance_values_list,
                    'attended_sessions': enrollment.total_attended or 0,
                    'missed_sessions': enrollment.total_non_attended or 0,
                    'total_sessions': enrollment.total_teaching_sessions or 0,
                })
            
            context = {
                'student': student,
                'enrollment_data': enrollment_data,
                'query': query,
                'search_type': search_type,
                'found': True
            }
            
            return render(request, 'analytics/search_results.html', context)
            
        except Student.DoesNotExist:
            return render(request, 'analytics/search_results.html', {
                'error': f'Student with ID "{query}" not found.',
                'query': query,
                'search_type': search_type,
                'found': False
            })
    
    elif search_type == 'course':
        try:
            course = Course.objects.get(code=query)
            
            enrollments = Enrollment.objects.filter(course=course).select_related('student')
            
            total_students = enrollments.count()
            
            ug_students = enrollments.filter(student__level_of_study='UG').count()
            pgt_students = enrollments.filter(student__level_of_study='PGT').count()
            
            weekly_attendance = []
            week_labels = list(SNAPSHOT_LABELS.values())
            
            for date in SNAPSHOT_LABELS.keys():
                course_enrollment_ids = enrollments.values_list('id', flat=True)
                
                snaps = AttendanceSnapshot.objects.filter(
                    enrollment_id__in=course_enrollment_ids,
                    snapshot_date=date
                ).exclude(attendance_percent__isnull=True)
                
                values = [s.attendance_percent for s in snaps]
                avg = round(sum(values) / len(values), 2) if values else 0
                weekly_attendance.append(avg)
            
            
            attendance_values = []
            for enrollment in enrollments:
                snapshots = AttendanceSnapshot.objects.filter(
                    enrollment=enrollment
                ).exclude(attendance_percent__isnull=True)
                
                if snapshots.exists():
                    avg_attendance = snapshots.aggregate(Avg('attendance_percent'))['attendance_percent__avg']
                    attendance_values.append(avg_attendance)
            
            course_avg_attendance = round(sum(attendance_values) / len(attendance_values), 2) if attendance_values else 0
            low_attendance_count = sum(1 for v in attendance_values if v < 75)
            
            context = {
                'course': course,
                'total_students': total_students,
                'ug_students': ug_students,
                'pgt_students': pgt_students,
                'course_avg_attendance': course_avg_attendance,
                'low_attendance_count': low_attendance_count,
                'weekly_attendance': weekly_attendance,
                'week_labels': week_labels,
                'query': query,
                'search_type': search_type,
                'found': True
            }
            
            return render(request, 'analytics/search_results.html', context)
            
        except Course.DoesNotExist:
            return render(request, 'analytics/search_results.html', {
                'error': f'Course with code "{query}" not found.',
                'query': query,
                'search_type': search_type,
                'found': False
            })
    
    return render(request, 'analytics/search_results.html', {
        'error': 'Invalid search type.',
        'query': query,
        'search_type': search_type,
        'found': False
    })




