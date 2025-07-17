from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # ug view
    path('ug-years/', views.ug_year_selection, name='ug_year_selection'),
    path('analytics/ug-year/<int:year>/', views.course_overview_by_year, name='course_overview_by_year'),
    path('course/<str:course_code>/<int:year>/', views.course_student_list, name='course_students'),
    path('course/<str:course_code>/year/<int:year>/student/<str:student_id>/', views.student_attendance_details, name='student_attendance_details'),

    # Pg views
    path('pg-years/', views.pg_year_selection, name='pg_year_selection'),
    path('analytics/pg-year/<int:year>/', views.course_overview_by_year_pg, name='course_overview_by_year_pg'),
    path('pg/course/<str:course_code>/<int:year>/', views.course_student_list_pg, name='course_students_pg'),
    path('pg/course/<str:course_code>/year/<int:year>/student/<str:student_id>/', views.student_attendance_details_pg, name='student_attendance_details'),
    

] 