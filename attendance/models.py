from django.conf import settings
from django.db import models

class Attendance(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

    attendance_date = models.DateField()
    status = models.CharField(max_length=10,
        choices=[("PENDING", "Pending"),("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),],default="PENDING",)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-attendance_date"]
        constraints = [models.UniqueConstraint(
                fields=["student", "attendance_date"],
                name="unique_student_attendance_per_day",)]