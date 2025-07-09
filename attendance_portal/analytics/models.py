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
    

    class Meta:
        unique_together = ('student', 'course')  # prevent duplicate enrollments

    def __str__(self):
        return f"{self.student.user_id} → {self.course.code} ({self.registration_status})"


class Attendance(models.Model):
    #enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)

    teaching_sessions = models.IntegerField(null=True, blank=True)
    total_attended = models.IntegerField(null=True, blank=True)
    non_attendance = models.IntegerField(null=True, blank=True)
    attendance_percent = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Attendance: {self.enrollment}"


class Assessment(models.Model):
    #enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)

    total_assessments = models.IntegerField(null=True, blank=True)
    submitted = models.IntegerField(null=True, blank=True)
    non_submission = models.IntegerField(null=True, blank=True)
    submitted_percent = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Assessment: {self.enrollment}"


class CourseTotalStats(models.Model):
    #enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)

    total_teaching_sessions = models.IntegerField(null=True, blank=True)
    total_attended = models.IntegerField(null=True, blank=True)
    total_non_attended = models.IntegerField(null=True, blank=True)
    total_attendance_percent = models.FloatField(null=True, blank=True)

    total_assessments = models.IntegerField(null=True, blank=True)
    total_submitted = models.IntegerField(null=True, blank=True)
    total_non_submission = models.IntegerField(null=True, blank=True)
    total_submitted_percent = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"TotalStats: {self.course.code}"
