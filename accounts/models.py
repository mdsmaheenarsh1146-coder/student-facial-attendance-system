from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    role = models.CharField(max_length=20,choices=[("STUDENT", "Student"),("ADMIN", "Admin"),("SUPERADMIN", "Superadmin"),],default="STUDENT",)
    is_approved = models.BooleanField(default=False)
    face_image = models.ImageField(upload_to="student_faces/",blank=False,null=False,)

    def __str__(self):
        return self.username