from django.shortcuts import render
from django.db.models import Avg, Count, F
from .models import Student, Course, Attendance, Assessment, CourseTotalStats, Enrollment
from django.db.models.functions import TruncDate
from django.contrib.auth.decorators import login_required
import json

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
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

def get_status(avg_attendance):
    if avg_attendance >= 85:
        return "Excellent"
    elif 75 <= avg_attendance < 85:
        return "Good"
    elif 65 <= avg_attendance < 75:
        return "Monitor"
    else:
        return "Critical"
    
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

        # Optional helper function
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


@login_required
def student_list(request):
    return render(request, 'analytics/student_list.html') 

@login_required
def course_overview(request):
    return render(request, 'analytics/course_overview.html')



@login_required
def student_detail(request):
    return render(request, 'analytics/student_detail.html')



