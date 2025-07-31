from django.db import models

class Student(models.Model):
    user_id = models.CharField(max_length=50, unique=True)
    level_of_study = models.CharField(max_length=10, choices=[
        ('UG', 'Undergraduate'),
        ('PG', 'Postgraduate')
    ])
    year_of_course = models.IntegerField()

    def __str__(self):
        return self.user_id


class Course(models.Model):
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.code} - {self.title}"


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    total_assessments = models.IntegerField(null=True, blank=True)
    total_attendance_percent = models.FloatField(null=True, blank=True)
    total_attended = models.IntegerField(null=True, blank=True)
    total_non_attended = models.IntegerField(null=True, blank=True)
    total_non_submission = models.IntegerField(null=True, blank=True)
    total_submitted = models.IntegerField(null=True, blank=True)
    total_submitted_percent = models.FloatField(null=True, blank=True)
    total_teaching_sessions = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'course')  

    def __str__(self):
        return f"{self.student.user_id} → {self.course.code}"




class AttendanceSnapshot(models.Model):
    enrollment = models.ForeignKey('Enrollment', on_delete=models.CASCADE)
    snapshot_date = models.DateField()
    teaching_sessions = models.IntegerField(null=True, blank=True)
    attended = models.IntegerField(null=True, blank=True)
    non_attended = models.IntegerField(null=True, blank=True)
    attendance_percent = models.FloatField(null=True, blank=True)
    assessments_total = models.IntegerField(null=True, blank=True)
    assessments_submitted = models.IntegerField(null=True, blank=True)
    assessments_non_submitted = models.IntegerField(null=True, blank=True)
    assessment_submitted_percent = models.FloatField(null=True, blank=True)
    last_attendance_datetime = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.enrollment.student.user_id} @ {self.snapshot_date}"  

