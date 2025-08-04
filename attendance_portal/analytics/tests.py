from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Student, Course, Enrollment, AttendanceSnapshot
from decimal import Decimal
from datetime import date

class AnalyticsViewsTest(TestCase):
    """
    Tests for analytics views 
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            password='tester123'
        )
        self.client = Client()
        self.client.login(username='tester', password='tester123')
        
        self.course_ug = Course.objects.create(
            code='G4010U',
            title='Test UG Course'
        )
        self.course_pg = Course.objects.create(
            code='G5009P',
            title='Test PGT Course'
        )
        
        self.student_ug_good = Student.objects.create(
            user_id='43402496',
            level_of_study='UG',
            year_of_course=1
        )
        self.student_ug_poor = Student.objects.create(
            user_id='43402497',
            level_of_study='UG',
            year_of_course=1
        )
        self.student_pg_good = Student.objects.create(
            user_id='43402498',
            level_of_study='PGT',
            year_of_course=1
        )
        self.student_pg_poor = Student.objects.create(
            user_id='43402499',
            level_of_study='PGT',
            year_of_course=1
        )
        
        self.enrollment_ug_good = Enrollment.objects.create(
            student=self.student_ug_good,
            course=self.course_ug,
            total_attendance_percent=85.0,
            total_attended=17,
            total_non_attended=3,
            total_teaching_sessions=20
        )
        self.enrollment_ug_poor = Enrollment.objects.create(
            student=self.student_ug_poor,
            course=self.course_ug,
            total_attendance_percent=65.0,
            total_attended=13,
            total_non_attended=7,
            total_teaching_sessions=20
        )
        self.enrollment_pg_good = Enrollment.objects.create(
            student=self.student_pg_good,
            course=self.course_pg,
            total_attendance_percent=90.0,
            total_attended=18,
            total_non_attended=2,
            total_teaching_sessions=20
        )
        self.enrollment_pg_poor = Enrollment.objects.create(
            student=self.student_pg_poor,
            course=self.course_pg,
            total_attendance_percent=60.0,
            total_attended=12,
            total_non_attended=8,
            total_teaching_sessions=20
        )
        
        snapshot_dates = [
            date(2017, 9, 25),  # W1
            date(2017, 10, 16), # W2
            date(2017, 11, 6),  # W3
            date(2017, 11, 27), # W4
        ]
        
        for i, snap_date in enumerate(snapshot_dates):
            AttendanceSnapshot.objects.create(
                enrollment=self.enrollment_ug_good,
                snapshot_date=snap_date,
                attendance_percent=85.0 + i,  
                attended=17,
                non_attended=3,
                teaching_sessions=20
            )
        
        for i, snap_date in enumerate(snapshot_dates):
            AttendanceSnapshot.objects.create(
                enrollment=self.enrollment_ug_poor,
                snapshot_date=snap_date,
                attendance_percent=65.0 - i,  
                attended=13,
                non_attended=7,
                teaching_sessions=20
            )
        
        for i, snap_date in enumerate(snapshot_dates):
            AttendanceSnapshot.objects.create(
                enrollment=self.enrollment_pg_good,
                snapshot_date=snap_date,
                attendance_percent=90.0 + i,  
                attended=18,
                non_attended=2,
                teaching_sessions=20
            )
        
        for i, snap_date in enumerate(snapshot_dates):
            AttendanceSnapshot.objects.create(
                enrollment=self.enrollment_pg_poor,
                snapshot_date=snap_date,
                attendance_percent=60.0 - i,  
                attended=12,
                non_attended=8,
                teaching_sessions=20
            )

    def test_dashboard_view(self):
        
        response = self.client.get(reverse('analytics:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        
        self.assertTemplateUsed(response, 'analytics/dashboard.html')
        
        context = response.context
        self.assertIn('ug_student_count', context)
        self.assertIn('pg_student_count', context)
        self.assertIn('ug_course_count', context)
        self.assertIn('pg_course_count', context)
        self.assertIn('avg_ug_attendance', context)
        self.assertIn('avg_pg_attendance', context)
        self.assertIn('low_attendance_ug_count', context)
        self.assertIn('low_attendance_pg_count', context)
        
        self.assertEqual(context['ug_student_count'], 2)  
        self.assertEqual(context['pg_student_count'], 2)  
        self.assertEqual(context['ug_course_count'], 1)  
        self.assertEqual(context['pg_course_count'], 1)   
        self.assertEqual(context['low_attendance_ug_count'], 1)  
        self.assertEqual(context['low_attendance_pg_count'], 1)  

    def test_ug_year_selection_view(self):
        
        response = self.client.get(reverse('analytics:ug_year_selection'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/ug_year_selection.html')
        
        context = response.context
        self.assertIn('year_data', context)
        
        
        year_1_data = None
        for year_data in context['year_data']:
            if year_data['year'] == 1:
                year_1_data = year_data
                break
        
        self.assertIsNotNone(year_1_data)
        self.assertEqual(year_1_data['student_count'], 2)
        self.assertEqual(year_1_data['course_count'], 1)
       
        self.assertEqual(year_1_data['avg_attendance'], 75.0)
        self.assertEqual(year_1_data['low_attendance_count'], 1)
        self.assertEqual(year_1_data['status'], 'Good')  

    def test_pg_year_selection_view(self):
        
        response = self.client.get(reverse('analytics:pg_year_selection'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/pg_year_selection.html')
        
        context = response.context
        self.assertIn('year_data', context)
        
        
        year_1_data = None
        for year_data in context['year_data']:
            if year_data['year'] == 1:
                year_1_data = year_data
                break
        
        self.assertIsNotNone(year_1_data)
        self.assertEqual(year_1_data['student_count'], 2)
        self.assertEqual(year_1_data['course_count'], 1)
        
        self.assertEqual(year_1_data['avg_attendance'], 75.0)
        self.assertEqual(year_1_data['low_attendance_count'], 1)
        self.assertEqual(year_1_data['status'], 'Good')  

    def test_course_overview_by_year_ug(self):
        
        response = self.client.get(reverse('analytics:course_overview_by_year', args=[1]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/course_overview.html')
        
        context = response.context
        self.assertIn('courses', context)
        self.assertEqual(len(context['courses']), 1)  
        
        course_data = context['courses'][0]
        self.assertEqual(course_data['code'], 'G4010U')
        self.assertEqual(course_data['title'], 'Test UG Course')
        self.assertEqual(course_data['student_count'], 2)
        self.assertEqual(course_data['avg_attendance'], 75.0)
        self.assertEqual(course_data['status'], 'Monitor')
        
        self.assertIn('1 (50.0%)', course_data['low_attendance_display'])

    def test_course_overview_by_year_pg(self):
        
        response = self.client.get(reverse('analytics:course_overview_by_year_pg', args=[1]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/course_overview_pg.html')
        
        context = response.context
        self.assertIn('courses', context)
        self.assertEqual(len(context['courses']), 1)  
        
        course_data = context['courses'][0]
        self.assertEqual(course_data['code'], 'G5009P')
        self.assertEqual(course_data['title'], 'Test PGT Course')
        self.assertEqual(course_data['student_count'], 2)
        self.assertEqual(course_data['avg_attendance'], 75.0)
        self.assertEqual(course_data['status'], 'Monitor')

    def test_course_student_list_ug(self):
        
        response = self.client.get(reverse('analytics:course_students', args=['G4010U', 1]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/course_students.html')
        
        context = response.context
        self.assertIn('students', context)
        self.assertEqual(len(context['students']), 2)
        
        
        students = context['students']
        self.assertEqual(students[0]['user_id'], '43402497')  
        self.assertEqual(students[0]['attendance'], 63.5)     
        self.assertEqual(students[1]['user_id'], '43402496')  
        self.assertEqual(students[1]['attendance'], 86.5)     

    def test_course_student_list_pg(self):
        
        response = self.client.get(reverse('analytics:course_students_pg', args=['G5009P', 1]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/course_students_pg.html')
        
        context = response.context
        self.assertIn('students', context)
        self.assertEqual(len(context['students']), 2)
        
        
        students = context['students']
        self.assertEqual(students[0]['user_id'], '43402499')  
        self.assertEqual(students[0]['attendance'], 58.5)     
        self.assertEqual(students[1]['user_id'], '43402498')  
        self.assertEqual(students[1]['attendance'], 91.5)     

    def test_student_attendance_details_ug(self):
       
        response = self.client.get(reverse('analytics:student_attendance_details', 
                                         args=['G4010U', 1, '43402496']))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/student_detail.html')
        
        context = response.context
        self.assertIn('student', context)
        self.assertIn('course', context)
        self.assertIn('student_attendance', context)
        self.assertIn('course_average', context)
        self.assertIn('week_labels', context)
        self.assertIn('attendance_values', context)
        
        
        self.assertEqual(context['student'].user_id, '43402496')
        self.assertEqual(context['course'].code, 'G4010U')
        self.assertEqual(context['student_attendance'], 86.5)  
        self.assertEqual(len(context['week_labels']), 4)     
        self.assertEqual(len(context['attendance_values']), 4) 

    def test_student_attendance_details_pg(self):
        
        response = self.client.get(reverse('analytics:student_attendance_details_pg', 
                                         args=['G5009P', 1, '43402498']))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/student_detail_pg.html')
        
        context = response.context
        self.assertIn('student', context)
        self.assertIn('course', context)
        self.assertIn('student_attendance', context)
        self.assertIn('course_average', context)
        
        
        self.assertEqual(context['student'].user_id, '43402498')
        self.assertEqual(context['course'].code, 'G5009P')
        self.assertEqual(context['student_attendance'], 91.5)  

    def test_search_student_found(self):
        
        response = self.client.get(reverse('analytics:search_view'), {
            'query': '43402496',
            'search_type': 'student'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/search_results.html')
        
        context = response.context
        self.assertTrue(context['found'])
        self.assertIn('student', context)
        self.assertIn('enrollment_data', context)
        self.assertEqual(context['student'].user_id, '43402496')
        self.assertEqual(len(context['enrollment_data']), 1)  

    def test_search_student_not_found(self):
        
        response = self.client.get(reverse('analytics:search_view'), {
            'query': '99999999',
            'search_type': 'student'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/search_results.html')
        
        context = response.context
        self.assertFalse(context['found'])
        self.assertIn('error', context)
        self.assertIn('Student with ID "99999999" not found', context['error'])

    def test_search_course_found(self):
       
        response = self.client.get(reverse('analytics:search_view'), {
            'query': 'G4010U',
            'search_type': 'course'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/search_results.html')
        
        context = response.context
        self.assertTrue(context['found'])
        self.assertIn('course', context)
        self.assertEqual(context['course'].code, 'G4010U')
        self.assertEqual(context['total_students'], 2)

    def test_search_course_not_found(self):
        
        response = self.client.get(reverse('analytics:search_view'), {
            'query': 'INVALID',
            'search_type': 'course'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/search_results.html')
        
        context = response.context
        self.assertFalse(context['found'])
        self.assertIn('error', context)
        self.assertIn('Course with code "INVALID" not found', context['error'])

    def test_attendance_status_calculation(self):
        
        self.assertEqual(self.enrollment_ug_good.total_attendance_percent, 85.0)
        self.assertEqual(self.enrollment_ug_poor.total_attendance_percent, 65.0)
        self.assertEqual(self.enrollment_pg_good.total_attendance_percent, 90.0)
        self.assertEqual(self.enrollment_pg_poor.total_attendance_percent, 60.0)
        
        
        def get_status(avg_attendance):
            if avg_attendance >= 85:
                return "Excellent"
            elif 75 <= avg_attendance < 85:
                return "Good"
            elif 65 <= avg_attendance < 75:
                return "Monitor"
            else:
                return "Critical"
        
        
        self.assertEqual(get_status(85.0), "Excellent")
        self.assertEqual(get_status(80.0), "Good")
        self.assertEqual(get_status(75.0), "Good")  
        self.assertEqual(get_status(70.0), "Monitor")
        self.assertEqual(get_status(60.0), "Critical")

    def test_authentication_required(self):
        
        
        self.client.logout()
        
        
        response = self.client.get(reverse('analytics:dashboard'))
        
        
        self.assertEqual(response.status_code, 302)  # Redirect status
        self.assertIn('/accounts/login/', response.url)

    def test_invalid_urls(self):
        
        
        response = self.client.get(reverse('analytics:student_attendance_details', 
                                         args=['G4010U', 1, 'INVALID']))
        self.assertEqual(response.status_code, 404)
        
        
        response = self.client.get(reverse('analytics:course_students', 
                                         args=['INVALID', 1]))
        self.assertEqual(response.status_code, 404)
