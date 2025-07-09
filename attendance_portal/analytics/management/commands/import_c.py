from django.core.management.base import BaseCommand
from analytics.models import Student
import pandas as pd

class Command(BaseCommand):
    help = 'Delete existing Student data and import all rows from new.xlsx, including Year = 0'

    def handle(self, *args, **kwargs):
        # Delete existing data
        Student.objects.all().delete()
        self.stdout.write(self.style.WARNING('Deleted all existing Student records.'))

        # Load Excel
        file_path = 'C:/Users/rahul/Desktop/msc final year project/Analyze_It/Data/new.xlsx'  # Update if needed
        df = pd.read_excel(file_path)

        skipped = 0
        imported = 0

        for _, row in df.iterrows():
            try:
                user_id = str(row['User']).strip()
                level = str(row['Level of Study']).strip()
                year = int(row['Year of Course'])  # will include 0

                if level not in ['UG', 'PG']:  # optional filter
                    print(f"⚠️ Skipping invalid level: {user_id} - {level}")
                    skipped += 1
                    continue

                Student.objects.create(
                    user_id=user_id,
                    level_of_study=level,
                    year_of_course=year
                )
                imported += 1
            except Exception as e:
                print(f"❌ Failed to import row: {row} - Error: {e}")
                skipped += 1

        self.stdout.write(self.style.SUCCESS(f'Imported: {imported} students'))
        self.stdout.write(self.style.WARNING(f'Skipped: {skipped} rows'))
