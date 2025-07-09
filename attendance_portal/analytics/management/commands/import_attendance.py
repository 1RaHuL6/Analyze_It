import pandas as pd
from django.core.management.base import BaseCommand
from django.utils import timezone
from analytics.models import Student, Course, Attendance, Assessment, CourseTotalStats

class Command(BaseCommand):
    help = 'Import attendance, assessment, and course total stats data from Excel file'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Path to the Excel file')

    def handle(self, *args, **options):
        print('DEBUG: import_attendance script started')
        excel_file = options['excel_file']
        
        try:
            self.stdout.write(f"Reading Excel file: {excel_file}")
            df = pd.read_excel(excel_file)
            print(f'DEBUG: DataFrame loaded with shape {df.shape}')
            df = df.dropna(how='all')
            self.stdout.write("Found columns: " + ", ".join(df.columns.tolist()))

            # Helper functions
            def safe_int(value, default=0):
                try:
                    return int(value) if pd.notna(value) else default
                except Exception:
                    return default
            def safe_float(value, default=0.0):
                try:
                    return float(value) if pd.notna(value) else default
                except Exception:
                    return default

            # 1. Import Assessment data
            assessment_count = 0
            for index, row in df.iterrows():
                try:
                    student_id = str(row.get('User', '')).strip()
                    course_code = str(row.get('Course Code', '')).strip()
                    if not student_id or not course_code or pd.isna(student_id) or pd.isna(course_code):
                        continue
                    student = Student.objects.filter(user_id=student_id).first()
                    course = Course.objects.filter(code=course_code).first()
                    if not student or not course:
                        continue
                    Assessment.objects.update_or_create(
                        student=student,
                        course=course,
                        defaults={
                            'total_assessments': safe_int(row.get('Assessments', 0)),
                            'submitted': safe_int(row.get('Assessments submitted', 0)),
                            'non_submission': safe_int(row.get('Non Submission', 0)),
                            'submitted_percent': safe_float(row.get('% Submitted', 0.0)),
                        }
                    )
                    assessment_count += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Assessment row {index+1} error: {e}"))
            self.stdout.write(self.style.SUCCESS(f'Imported/updated {assessment_count} assessment records.'))

            # 2. Import Attendance data
            attendance_count = 0
            for index, row in df.iterrows():
                try:
                    student_id = str(row.get('User', '')).strip()
                    course_code = str(row.get('Course Code', '')).strip()
                    if not student_id or not course_code or pd.isna(student_id) or pd.isna(course_code):
                        continue
                    student = Student.objects.filter(user_id=student_id).first()
                    course = Course.objects.filter(code=course_code).first()
                    if not student or not course:
                        continue
                    Attendance.objects.update_or_create(
                        student=student,
                        course=course,
                        defaults={
                            'teaching_sessions': safe_int(row.get('Teaching Sessions', 0)),
                            'total_attended': safe_int(row.get('Total attended', 0)),
                            'non_attendance': safe_int(row.get('Non Attendance', 0)),
                            'attendance_percent': safe_float(row.get('% Attendance', 0.0)),
                        }
                    )
                    attendance_count += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Attendance row {index+1} error: {e}"))
            self.stdout.write(self.style.SUCCESS(f'Imported/updated {attendance_count} attendance records.'))

            # 3. Import CourseTotalStats data (rows 2-1266, i.e., index 1-1265)
            stats_count = 0
            for index, row in df.iloc[1:1266].iterrows():
                try:
                    course_code = str(row.get('Course Code', '')).strip()
                    if not course_code or pd.isna(course_code):
                        continue
                    course = Course.objects.filter(code=course_code).first()
                    if not course:
                        continue
                    CourseTotalStats.objects.update_or_create(
                        course=course,
                        defaults={
                            'total_teaching_sessions': safe_int(row.get('Total Teaching Sessions', 0)),
                            'total_attended': safe_int(row.get('Attended Total', 0)),
                            'total_non_attended': safe_int(row.get('Total Non Attended', 0)),
                            'total_attendance_percent': safe_float(row.get('Total % Attendance', 0.0)),
                            'total_assessments': safe_int(row.get('Total Assessment', 0)),
                            'total_submitted': safe_int(row.get('Total Assessments submitted', 0)),
                            'total_non_submission': safe_int(row.get('Total Non submission', 0)),
                            'total_submitted_percent': safe_float(row.get('Total Assessment Submitted', 0.0)),
                        }
                    )
                    stats_count += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"CourseTotalStats row {index+1} error: {e}"))
            self.stdout.write(self.style.SUCCESS(f'Imported/updated {stats_count} course total stats records.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing data: {str(e)}')) 