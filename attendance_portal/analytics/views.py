from django.shortcuts import render
from django.db.models import Avg, Count, F
from .models import Student, Course, Attendance, Assessment, CourseTotalStats
from django.db.models.functions import TruncDate
from django.contrib.auth.decorators import login_required
import json

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
     ug_student_count = Student.objects.filter(level_of_study='UG').count()
     ug_course_count = Course.objects.filter(
        enrollment__student__level_of_study='UG'
    ).distinct().count()
     pg_student_count = Student.objects.filter(level_of_study='PG').count()
     pg_course_count = Course.objects.filter(
        enrollment__student__level_of_study='PG'
    ).distinct().count()
     context = {
        'ug_student_count': ug_student_count,
        'ug_course_count': ug_course_count,
        'pg_student_count': pg_student_count,
        'pg_course_count': pg_course_count
        
    }
     return render(request, 'analytics/dashboard.html', context)

@login_required
def ug_year_selection(request):
    return render(request, 'analytics/ug_year_selection.html')

@login_required
def course_overview(request):
    return render(request, 'analytics/course_overview.html')

@login_required
def student_list(request):
    return render(request, 'analytics/student_list.html')

@login_required
def student_detail(request):
    return render(request, 'analytics/student_detail.html')



