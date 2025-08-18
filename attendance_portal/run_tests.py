import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_portal.settings')
    django.setup()

def run_tests():
    """Run the test suite"""
    print("🧪 Starting Automated Tests for Analytics Views...")
    print("=" * 60)
    
    execute_from_command_line(['manage.py', 'test', 'analytics.tests', '--verbosity=2'])

if __name__ == '__main__':
    setup_django()
    run_tests()
    print("\n Tests completed") 