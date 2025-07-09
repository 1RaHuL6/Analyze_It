from django.core.management.base import BaseCommand
from analytics.models import Assessment, Attendance, CourseTotalStats

class Command(BaseCommand):
    help = 'Clear all data from Assessment, Attendance, and CourseTotalStats tables.'

    def handle(self, *args, **options):
        Assessment.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Cleared Assessment table.'))
        Attendance.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Cleared Attendance table.'))
        CourseTotalStats.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Cleared CourseTotalStats table.')) 