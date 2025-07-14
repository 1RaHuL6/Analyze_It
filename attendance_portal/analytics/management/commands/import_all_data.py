from django.core.management.base import BaseCommand
from analytics.models import Student, Course, Enrollment
import pandas as pd

class Command(BaseCommand):
    help = 'Import all data (students, enrollments with stats) from Excel file (courses must already exist)'

    def handle(self, *args, **kwargs):
        file_path = 'C:/Users/rahul/Desktop/msc final year project/Analyze_It/Data/new.xlsx'  # Update path if needed
        df = pd.read_excel(file_path)

        count_students = 0
        count_enrollments = 0
        for _, row in df.iterrows():
            user_id = str(row['User']).strip()
            level = row['Level of Study'].strip()
            year = int(row['Year of Course'])
            course_code = row['Course Code'].strip()

            # Get or create student
            student, _ = Student.objects.get_or_create(
                user_id=user_id,
                defaults={
                    'level_of_study': level,
                    'year_of_course': year
                }
            )
            count_students += 1

            # Get course (do not create)
            try:
                course = Course.objects.get(code=course_code)
            except Course.DoesNotExist:
                print(f"⚠️ Skipping: Course not found for code {course_code} (student {user_id})")
                continue

            # Create or update enrollment with stats
            Enrollment.objects.update_or_create(
                student=student,
                course=course,
                defaults={
                    'total_teaching_sessions': row.get('Total Teaching Sessions', None),
                    'total_attended': row.get('Attended Total', None),
                    'total_non_attended': row.get('Total Non Attended', None),
                    'total_attendance_percent': row.get('Total % Attendance', None),
                    'total_assessments': row.get('Total Assessment', None),
                    'total_submitted': row.get('Total Assessments submitted', None),
                    'total_non_submission': row.get('Total Non submission', None),
                    'total_submitted_percent': row.get('Total % Assessment Submitted', None),
                }
            )
            count_enrollments += 1
            print(f"Linked: {student.user_id} -> {course.code} (with stats)")

        self.stdout.write(self.style.SUCCESS(f'Successfully imported/updated {count_students} students and {count_enrollments} enrollments with stats.')) 