from django.core.management.base import BaseCommand
from analytics.models import Student, Course, AttendanceRecord

class Command(BaseCommand):
    help = 'Reset all data in the analytics models'

    def handle(self, *args, **options):
        # Delete all records in reverse order of dependencies
        self.stdout.write("Deleting all attendance records...")
        AttendanceRecord.objects.all().delete()
        
        self.stdout.write("Deleting all courses...")
        Course.objects.all().delete()
        
        self.stdout.write("Deleting all students...")
        Student.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('Successfully deleted all data')) 