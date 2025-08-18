from django.core.management.base import BaseCommand
from analytics.models import CourseTotalStats, Course
import pandas as pd
import os

class Command(BaseCommand):
    help = 'Import course total statistics from snapshot data by aggregating data by course.'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='Data/snapshot_data.xlsx', help='Path to the Excel file')

    def handle(self, *args, **options):
        excel_path = options['file']
        if not os.path.exists(excel_path):
            self.stdout.write(self.style.ERROR(f"File not found: {excel_path}"))
            return

        df = pd.read_excel(excel_path)
        self.stdout.write(f"Loaded {len(df)} rows from {excel_path}")
        
        
        course_stats = df.groupby('Course Code').agg({
            'Teaching Sessions': ['sum', 'max'],  
            'Attended_new': 'sum',
            'Non Attendance': 'sum', 
            '% Attendance': 'mean',  
            'Assessments': ['sum', 'max'],  
            'assessments_submitted': 'sum',
            'Non Submission': 'sum',
            '% Submitted': 'mean'  
        }).round(2)
        
       
        course_stats.columns = ['_'.join(col).strip() for col in course_stats.columns]
        
        created_count = 0
        updated_count = 0
        
        for course_code, stats in course_stats.iterrows():
            try:
                course = Course.objects.get(code=str(course_code).strip())
            except Course.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Course not found: {course_code}"))
                continue
                
        
            course_total_stats, created = CourseTotalStats.objects.update_or_create(
                course=course,
                defaults={
                    'total_teaching_sessions': int(stats.get('Teaching Sessions_max', 0)),
                    'total_attended': int(stats.get('Attended_new_sum', 0)),
                    'total_non_attended': int(stats.get('Non Attendance_sum', 0)),
                    'total_attendance_percent': float(stats.get('% Attendance_mean', 0)),
                    'total_assessments': int(stats.get('Assessments_max', 0)),
                    'total_submitted': int(stats.get('assessments_submitted_sum', 0)),
                    'total_non_submission': int(stats.get('Non Submission_sum', 0)),
                    'total_submitted_percent': float(stats.get('% Submitted_mean', 0)),
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"Created stats for course: {course_code}")
            else:
                updated_count += 1
                self.stdout.write(f"Updated stats for course: {course_code}")
        
        self.stdout.write(self.style.SUCCESS(
            f"Import completed! Created: {created_count}, Updated: {updated_count}, "
            f"Total courses processed: {created_count + updated_count}"
        )) 