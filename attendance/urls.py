from django.urls import path
from . import views

urlpatterns = [
    path("submit/",views.submit_attendance,name="submit_attendance",),
    path("success/",views.attendance_success,name="attendance_success",),
    path("history/",views.attendance_history,name="attendance_history",),
    path("attendance/approvals/",views.attendance_approvals,name="attendance_approvals"),
    path("attendance/approve/<int:attendance_id>/",views.approve_attendance,name="approve_attendance"),
     path( "reject/<int:attendance_id>/", views.reject_attendance, name="reject_attendance" ),  
]