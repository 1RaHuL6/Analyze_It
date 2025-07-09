from django.core.management.base import BaseCommand
from analytics.models import Student, Course, Enrollment  # adjust if needed
import pandas as pd

class Command(BaseCommand):
    help = 'Import enrollments from Excel file'

    def handle(self, *args, **kwargs):
        file_path = 'C:/Users/rahul/Desktop/msc final year project/Analyze_It/Data/new.xlsx'  # Update path if needed
        df = pd.read_excel(file_path)

        for _, row in df.iterrows():
            user_id = str(row['User']).strip()
            level = row['Level of Study'].strip()
            year = int(row['Year of Course'])
            course_title = row['Course Title'].strip()
            course_code = row['Course Code'].strip()

            # Get or create student
            student, _ = Student.objects.get_or_create(
                user_id=user_id,
                defaults={
                    'level_of_study': level,
                    'year_of_course': year
                }
            )

            # Get or create course
            course, _ = Course.objects.get_or_create(
                code=course_code,
                defaults={'title': course_title}
            )

            # Create enrollment (ignore registration_status)
            Enrollment.objects.get_or_create(
                student=student,
                course=course
            )

            print(f"Linked: {student.user_id} -> {course.code}")

        self.stdout.write(self.style.SUCCESS('Successfully imported enrollments (excluding registration status).'))
