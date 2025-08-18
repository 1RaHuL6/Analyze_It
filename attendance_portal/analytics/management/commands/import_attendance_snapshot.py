from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date, parse_datetime
from analytics.models import AttendanceSnapshot, Enrollment
import pandas as pd
import os

class Command(BaseCommand):
    help = 'Import attendance snapshot data from Excel into the AttendanceSnapshot model.'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='Data/snapshot_data.xlsx', help='Path to the Excel file')
        parser.add_argument('--clear', action='store_true', help='Clear existing snapshots before import')
        parser.add_argument('--dry-run', action='store_true', help='Run the script without importing data to check for issues.')

    def handle(self, *args, **options):
        excel_path = options['file']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.HTTP_INFO(' No data will be imported.'))
            
        if not os.path.exists(excel_path):
            self.stdout.write(self.style.ERROR(f"File not found: {excel_path}"))
            return

        if options['clear'] and not dry_run:
            AttendanceSnapshot.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing snapshots.'))

        df = pd.read_excel(excel_path)
        self.stdout.write(f"Loaded {len(df)} rows from {excel_path}")
        
        # Forward fill to handle missing dates
        df['snapshot_date'].ffill(inplace=True)
        self.stdout.write(self.style.HTTP_INFO("Applied forward fill."))

        snapshots = []
        errors = {
            'missing_enrollments': 0,
            'invalid_dates': 0,
            'missing_data': 0,
            'missing_enrollment_details': [],
            'invalid_date_details': []
        }

        for idx, row in df.iterrows():
            user_id = str(row['User']).strip() if pd.notna(row['User']) else None
            course_code = str(row['Course Code']).strip() if pd.notna(row['Course Code']) else None
            
            if not user_id or not course_code:
                errors['missing_data'] += 1
                continue

            try:
                
                Enrollment.objects.select_related('student', 'course').get(
                    student__user_id=user_id,
                    course__code=course_code
                )
            except Enrollment.DoesNotExist:
                errors['missing_enrollments'] += 1
                errors['missing_enrollment_details'].append({
                    'row': idx + 2,
                    'user_id': user_id,
                    'course_code': course_code
                })
                continue

           
            snapshot_date_val = row.get('snapshot_date')
            last_attendance_val = row.get('Last Attendence')
            
            try:
                
                snapshot_date = pd.to_datetime(snapshot_date_val, dayfirst=True).date() if pd.notna(snapshot_date_val) else None
                last_attendance = pd.to_datetime(last_attendance_val, dayfirst=True) if pd.notna(last_attendance_val) else None
                
                if not snapshot_date:
                    raise ValueError("Snapshot date is missing or invalid")

            except (ValueError, TypeError):
                errors['invalid_dates'] += 1
                errors['invalid_date_details'].append({
                    'row': idx + 2,
                    'snapshot_date': snapshot_date_val,
                    'last_attendance': last_attendance_val
                })
                continue 
            
            
            if not dry_run:
                snapshot = AttendanceSnapshot(
                    enrollment=Enrollment.objects.get(student__user_id=user_id, course__code=course_code), 
                    snapshot_date=snapshot_date,
                    teaching_sessions=int(row['Teaching Sessions']) if pd.notna(row['Teaching Sessions']) else None,
                    attended=int(row['Attended_new']) if pd.notna(row['Attended_new']) else None,
                    non_attended=int(row['Non Attendance']) if pd.notna(row['Non Attendance']) else None,
                    attendance_percent=float(row['% Attendance']) if pd.notna(row['% Attendance']) else None,
                    assessments_total=int(row['Assessments']) if pd.notna(row['Assessments']) else None,
                    assessments_submitted=int(row['assessments_submitted']) if pd.notna(row['assessments_submitted']) else None,
                    assessments_non_submitted=int(row['Non Submission']) if pd.notna(row['Non Submission']) else None,
                    assessment_submitted_percent=float(row['% Submitted']) if pd.notna(row['% Submitted']) else None,
                    last_attendance_datetime=last_attendance
                )
                snapshots.append(snapshot)
        
       
        if dry_run:
            self.stdout.write(self.style.SUCCESS('\nDry run summary:'))
            if errors['missing_enrollments'] > 0:
                self.stdout.write(self.style.WARNING(f"\nFound {errors['missing_enrollments']} missing enrollments "))
                for detail in errors['missing_enrollment_details']:
                    self.stdout.write(f"  - Row {detail['row']}: User ID '{detail['user_id']}', Course Code '{detail['course_code']}'")
            else:
                self.stdout.write(self.style.SUCCESS("\nNo missing enrollments found."))

            if errors['invalid_dates'] > 0:
                self.stdout.write(self.style.WARNING(f"\nFound {errors['invalid_dates']} rows with invalid dates:"))
                for detail in errors['invalid_date_details']:
                    self.stdout.write(f"  - Row {detail['row']}: snapshot_date='{detail['snapshot_date']}', last_attendance='{detail['last_attendance']}'")
            else:
                self.stdout.write(self.style.SUCCESS("\nNo date issues found."))
            
            self.stdout.write(f"\nRows with other missing data: {errors['missing_data']}")
            return

        
        if snapshots:
            batch_size = 500
            total_batches = (len(snapshots) + batch_size - 1) // batch_size
            
            for i in range(0, len(snapshots), batch_size):
                batch = snapshots[i:i + batch_size]
                AttendanceSnapshot.objects.bulk_create(batch)
                self.stdout.write(f"Imported batch {(i // batch_size) + 1} of {total_batches}")

        self.stdout.write(self.style.SUCCESS(
            f"\nImport Complete!\n"
            f" Successfully imported: {len(snapshots)} snapshots\n"
            f"- Skipped missing enrollments: {errors['missing_enrollments']}\n"
            f" Skipped invalid dates: {errors['invalid_dates']}\n"
            f" Skipped missing data: {errors['missing_data']}\n"
        ))
        if errors['missing_enrollment_details']:
            self.stdout.write(self.style.WARNING("\nDetails of skipped missing enrollments:"))
            for detail in errors['missing_enrollment_details']:
                self.stdout.write(f"  - Row {detail['row']}: User ID '{detail['user_id']}', Course Code '{detail['course_code']}'")
