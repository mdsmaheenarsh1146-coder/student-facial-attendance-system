from django.shortcuts import render, redirect
from .forms import StudentSignupForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import get_user_model
from django.contrib import messages

def student_signup(request):
    if request.method == "POST":
        form = StudentSignupForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect("signup_success")

    else:
        form = StudentSignupForm()

    return render(request, "accounts/signup.html", {"form": form})

def signup_success(request):
    return render(request, "accounts/signup_success.html")



def user_login(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()

        if not user.is_approved:
            form.add_error(None, "Your account is waiting for approval.")
        else:
            login(request, user)
            return redirect("home")

    return render(request, "accounts/login.html", {"form": form})

def home(request):
    return render(request, "accounts/home.html")


def user_logout(request):
    logout(request)
    return redirect("home")

@login_required
def user_profile(request):
    return render(request, "accounts/user_profile.html")


from .models import User
@login_required
def student_approvals(request):
    if request.user.role != 'SUPERADMIN':
        return redirect("home")

    pending_students = User.objects.filter(role='STUDENT',is_approved=False,)

    return render(request,"accounts/student_approvals.html",{"pending_students": pending_students},)
    

@login_required
def approve_student(request, user_id):
    if request.user.role != 'SUPERADMIN':
        return redirect("home")

    if request.method == "POST":
        student = User.objects.get(id=user_id,role='STUDENT',)

        student.is_approved = True
        student.save()
    return redirect("student_approvals")


# Reject a pending student
@login_required
@require_POST
def reject_student(request, user_id):
    if request.user.role != "SUPERADMIN":
        return redirect("home")

    student = get_object_or_404(
        User,
        id=user_id,
        role="STUDENT",
        is_approved=False
    )

    student.delete()

    return redirect("student_approvals")


# Show all users
@login_required
def all_users(request):
    if request.user.role != "SUPERADMIN":
        return redirect("home")

    users = User.objects.all().order_by("username")

    return render(
        request,
        "accounts/all_users.html",
        {"users": users}
    )


# Delete a user
@login_required
@require_POST
def delete_user(request, user_id):
    if request.user.role != "SUPERADMIN":
        return redirect("home")

    user = get_object_or_404(User, id=user_id)

    # Prevent deleting your own account or another superadmin
    if user.id == request.user.id or user.role == "SUPERADMIN":
        return redirect("all_users")

    user.delete()

    return redirect("all_users")


@login_required
def edit_user(request, user_id):
    if request.user.role != "SUPERADMIN":
        return redirect("home")

    user = get_object_or_404(User, id=user_id)

    if user.role == "SUPERADMIN" and user.id != request.user.id:
        messages.error(request, "You cannot edit another Superadmin.")
        return redirect("all_users")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not username or not email:
            messages.error(request, "Username and email are required.")
        elif User.objects.filter(username=username).exclude(id=user.id).exists():
            messages.error(request, "This username is already taken.")
        elif User.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, "This email is already registered.")
        else:
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.email = email

            if password:
                user.set_password(password)

            user.save()
            messages.success(request, "User details updated successfully.")
            return redirect("all_users")

    return render(
        request,
        "accounts/edit_user.html",
        {"edit_user": user}
    )

