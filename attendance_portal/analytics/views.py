from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Count, F
from .models import Student, Course, Attendance, Assessment, CourseTotalStats, Enrollment
from django.db.models.functions import TruncDate
from django.contrib.auth.decorators import login_required
import json

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
     
     avg_ug_attendance = Enrollment.objects.filter( student__level_of_study='UG').aggregate(avg=Avg('total_attendance_percent')
    )['avg'] or 0  
     avg_ug_attendance = round(avg_ug_attendance, 2)
    
     avg_pg_attendance = Enrollment.objects.filter( student__level_of_study='PGT').aggregate(avg=Avg('total_attendance_percent')
    )['avg'] or 0  
     avg_pg_attendance = round(avg_pg_attendance, 2)
     
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
        'low_attendance_pg_count': low_attendance_pg_count
         
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
  
# level 2 UG    
@login_required
def ug_year_selection(request):
    year_data = []

    for year in range(6):  # 0 to 5 years, as number of years will remain same
        students = Student.objects.filter(level_of_study='UG', year_of_course=year)
        student_ids = students.values_list('id', flat=True)

        enrollments = Enrollment.objects.filter(student_id__in=student_ids)

        student_count = students.count()

        # Extract non-null attendance values
        attendance_values = enrollments.exclude(total_attendance_percent__isnull=True).values_list('total_attendance_percent', flat=True)
        avg_attendance = sum(attendance_values) / len(attendance_values) if attendance_values else 0

        # Count students with < 75% average attendance
        low_attendance_count = enrollments.filter(total_attendance_percent__lt=75).count()

        year_data.append({
            'year': year,
            'description': YEAR_DESCRIPTIONS.get(year, f"Year {year}"),
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

    for year in range(1,3):  # 1 to 2 years, as number of years will remain same
        students = Student.objects.filter(level_of_study='PGT', year_of_course=year)
        student_ids = students.values_list('id', flat=True)

        enrollments = Enrollment.objects.filter(student_id__in=student_ids)

        student_count = students.count()

        # Extract non-null attendance values
        attendance_values = enrollments.exclude(total_attendance_percent__isnull=True).values_list('total_attendance_percent', flat=True)
        avg_attendance = sum(attendance_values) / len(attendance_values) if attendance_values else 0

        # Count students with < 75% average attendance
        low_attendance_count = enrollments.filter(total_attendance_percent__lt=75).count()

        year_data.append({
            'year': year,
            'description': YEAR_DESCRIPTIONS.get(year, f"Year {year}"),
            'student_count': student_count,
            'avg_attendance': round(avg_attendance, 2),
            'low_attendance_count': low_attendance_count,
            'status': get_status(avg_attendance),
        })

    context = {
        'year_data': year_data,
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
        attendance_values = course_enrollments.exclude(total_attendance_percent__isnull=True).values_list('total_attendance_percent', flat=True)
        avg_attendance = sum(attendance_values) / len(attendance_values) if attendance_values else 0
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
            'avg_attendance': round(avg_attendance, 2),
            'low_attendance_display': f"{low_attendance_count} ({round((low_attendance_count / student_count) * 100, 1)}%)" if student_count else "0",
            'status': get_status(avg_attendance)
        })

    return render(request, "analytics/course_overview.html", {
        'year': year,
        'courses': course_data,
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
        attendance_values = course_enrollments.exclude(total_attendance_percent__isnull=True).values_list('total_attendance_percent', flat=True)
        avg_attendance = sum(attendance_values) / len(attendance_values) if attendance_values else 0
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
            'avg_attendance': round(avg_attendance, 2),
            'low_attendance_display': f"{low_attendance_count} ({round((low_attendance_count / student_count) * 100, 1)}%)" if student_count else "0",
            'status': get_status(avg_attendance)
        })

    return render(request, "analytics/course_overview_pg.html", {
        'year': year,
        'courses': course_data,
    })

#level 4 UG
@login_required
def course_student_list(request, course_code, year):
    course = get_object_or_404(Course, code=course_code)
    # Filter enrollments by both course and student's year
    enrollments = Enrollment.objects.filter(
        course__code=course_code,
        student__year_of_course=year
    ).select_related('student')
    
    student_data = [
        {
            'user_id': e.student.user_id,
            'attendance': e.total_attendance_percent if e.total_attendance_percent is not None else 'N/A',
            'year': e.student.year_of_course  # Include year in the context if needed
        }
        for e in enrollments
    ]
    
    back_url = request.META.get('HTTP_REFERER', '/')
    context = {
        'course': course,
        'students': student_data,
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
    
    student_data = [
        {
            'user_id': e.student.user_id,
            'attendance': e.total_attendance_percent if e.total_attendance_percent is not None else 'N/A',
            'year': e.student.year_of_course  # Include year in the context if needed
        }
        for e in enrollments
    ]
    
    back_url = request.META.get('HTTP_REFERER', '/')
    context = {
        'course': course,
        'students': student_data,
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

    # course-level statistics
    course_stats = CourseTotalStats.objects.filter(course=course).first()
    course_average = course_stats.total_attendance_percent if course_stats and course_stats.total_attendance_percent is not None else 0

    # student data 
    student_attendance = enrollment.total_attendance_percent or 0
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
    }
    return render(request, 'analytics/student_detail.html', context)

@login_required   
def student_attendance_details_pg(request, course_code, year, student_id):
    course = get_object_or_404(Course, code=course_code)
    student = get_object_or_404(Student, user_id=student_id, year_of_course=year)
    enrollment = get_object_or_404(Enrollment, course=course, student=student)

    # course-level statistics
    course_stats = CourseTotalStats.objects.filter(course=course).first()
    course_average = course_stats.total_attendance_percent if course_stats and course_stats.total_attendance_percent is not None else 0

    # student data 
    student_attendance = enrollment.total_attendance_percent or 0
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
    }
    return render(request, 'analytics/student_detail.html', context)





