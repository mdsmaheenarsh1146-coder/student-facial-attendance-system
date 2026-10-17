from django.urls import path

from . import views


urlpatterns = [
    path("signup/", views.student_signup, name="signup"),
    path("signup/success/", views.signup_success, name="signup_success"),
    path("login/", views.user_login, name="login"),
    path("", views.home, name="home"),
    path("logout/", views.user_logout, name="logout"),
    path("user/", views.user_profile, name="user_profile"),
    path("student-approvals/",views.student_approvals, name="student_approvals",),
    path("student-approvals/<int:user_id>/approve/",views.approve_student,name="approve_student",),
    path( "student-approvals/<int:user_id>/reject/", views.reject_student,name="reject_student",),
    path( "all-users/", views.all_users,name="all_users",),
    path("delete-user/<int:user_id>/",views.delete_user,name="delete_user",),
    path("edit-user/<int:user_id>/",views.edit_user,name="edit_user",),  

]
