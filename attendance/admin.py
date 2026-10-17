from django.contrib import admin

from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "attendance_date",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "attendance_date",
    )