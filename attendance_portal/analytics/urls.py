from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('ug-years/', views.ug_year_selection, name='ug_year_selection'),
    path('courses/', views.course_overview, name='course_overview'),
    path('students/', views.student_list, name='student_list'),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
] 