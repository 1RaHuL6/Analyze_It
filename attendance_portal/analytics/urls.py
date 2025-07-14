from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('ug-years/', views.ug_year_selection, name='ug_year_selection'),
    path('pg-years/', views.pg_year_selection, name='pg_year_selection'),
    path('analytics/ug-year/<int:year>/', views.course_overview_by_year, name='course_overview_by_year'),

] 