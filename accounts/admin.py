from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin
@admin.register(User)   #or admin.site.register(User, CustomUserAdmin)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Attendance System",{"fields":("role","is_approved","face_image",)},),)