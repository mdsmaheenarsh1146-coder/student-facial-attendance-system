import base64
import os

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import AttendanceForm
from .models import Attendance
from .face_utils import verify_face


# =========================================================
# STUDENT: SUBMIT ATTENDANCE
# =========================================================

@login_required
def submit_attendance(request):
    if request.user.role != "STUDENT":
        return redirect("home")

    today = timezone.localdate()

    # Check whether attendance has already been submitted today
    if Attendance.objects.filter(
        student=request.user,
        attendance_date=today
    ).exists():
        return render(
            request,
            "attendance/submit_attendance.html",
            {
                "form": AttendanceForm(),
                "error": "You have already submitted attendance today.",
            }
        )

    if request.method == "POST":
        form = AttendanceForm(request.POST)
        image_data = request.POST.get("face_image_data", "")

        # Check captured image
        if not image_data:
            return render(
                request,
                "attendance/submit_attendance.html",
                {
                    "form": form,
                    "error": (
                        "No captured image received. "
                        "Please capture your face again."
                    ),
                }
            )

        # Decode the Base64 image
        try:
            if "," in image_data:
                image_data = image_data.split(",", 1)[1]

            image_bytes = base64.b64decode(
                image_data,
                validate=True
            )

            if not image_bytes:
                raise ValueError("Empty image")

            image = ContentFile(
                image_bytes,
                name="captured_face.jpg"
            )

        except (ValueError, TypeError):
            return render(
                request,
                "attendance/submit_attendance.html",
                {
                    "form": form,
                    "error": (
                        "Unable to process the captured image. "
                        "Please capture your face again."
                    ),
                }
            )

        # Check registered face image
        if not request.user.face_image:
            return render(
                request,
                "attendance/submit_attendance.html",
                {
                    "form": form,
                    "error": (
                        "No registered face image found for your account."
                    ),
                }
            )

        try:
            reference_path = request.user.face_image.path

        except (ValueError, NotImplementedError):
            return render(
                request,
                "attendance/submit_attendance.html",
                {
                    "form": form,
                    "error": (
                        "Unable to access your registered face image. "
                        "Please contact the administrator."
                    ),
                }
            )

        if not os.path.exists(reference_path):
            return render(
                request,
                "attendance/submit_attendance.html",
                {
                    "form": form,
                    "error": (
                        "Your registered face image could not be found. "
                        "Please contact the administrator."
                    ),
                }
            )

        # Validate attendance form
        if not form.is_valid():
            return render(
                request,
                "attendance/submit_attendance.html",
                {
                    "form": form,
                    "error": (
                        "Please check the attendance form and try again."
                    ),
                }
            )

        # Verify face
        try:
            face_verified = verify_face(
                image,
                reference_path
            )

        except Exception as e:
            print("FACE VERIFICATION ERROR:", repr(e))

            return render(
                request,
                "attendance/submit_attendance.html",
                {
                    "form": form,
                    "error": (
                        "Unable to verify your face. "
                        "Please try again with good lighting "
                        "and your face clearly visible."
                    ),
                }
            )

        # Save attendance if face matches
        if face_verified:
            attendance = form.save(commit=False)
            attendance.student = request.user
            attendance.attendance_date = today
            attendance.status = "PENDING"
            attendance.save()

            return redirect("attendance_success")

        return render(
            request,
            "attendance/submit_attendance.html",
            {
                "form": form,
                "error": (
                    "Face verification failed. Make sure your face "
                    "is clearly visible and matches your registered image."
                ),
            }
        )

    return render(
        request,
        "attendance/submit_attendance.html",
        {
            "form": AttendanceForm(),
        }
    )


# =========================================================
# STUDENT: ATTENDANCE SUCCESS
# =========================================================

@login_required
def attendance_success(request):
    return render(
        request,
        "attendance/attendance_success.html"
    )


# =========================================================
# STUDENT: ATTENDANCE HISTORY
# =========================================================

@login_required
def attendance_history(request):
    if request.user.role != "STUDENT":
        return redirect("home")

    records = Attendance.objects.filter(
        student=request.user
    ).order_by("-attendance_date")

    return render(
        request,
        "attendance/attendance_history.html",
        {
            "records": records
        }
    )


# =========================================================
# ADMIN: VIEW ATTENDANCE APPROVALS
# =========================================================

@login_required
def attendance_approvals(request):
    if request.user.role not in ["ADMIN", "SUPERADMIN"]:
        return redirect("home")

    pending = Attendance.objects.filter(
        status="PENDING"
    ).order_by("-attendance_date")

    summary = {
        "pending": Attendance.objects.filter(
            status="PENDING"
        ).count(),

        "approved": Attendance.objects.filter(
            status="APPROVED"
        ).count(),

        "rejected": Attendance.objects.filter(
            status="REJECTED"
        ).count(),
    }

    return render(
        request,
        "attendance/attendance_approvals.html",
        {
            "pending_records": pending,
            "summary": summary,
        }
    )


# =========================================================
# ADMIN: APPROVE ATTENDANCE AND SEND EMAIL
# =========================================================

@login_required
@require_POST
def approve_attendance(request, attendance_id):
    # Only admins can approve attendance
    if request.user.role not in ["ADMIN", "SUPERADMIN"]:
        return redirect("home")

    attendance = get_object_or_404(
        Attendance,
        id=attendance_id
    )

    # Process only pending attendance
    if attendance.status == "PENDING":

        # Update attendance status
        attendance.status = "APPROVED"
        attendance.save(update_fields=["status"])

        # Get student's email address
        student_email = attendance.student.email

        if not student_email:
            print(
                "EMAIL ERROR: Student has no email address."
            )
            return redirect("attendance_approvals")

        # Send approval notification
        try:
            email_sent = send_mail(
                subject="Attendance Approved",
                message=(
                    f"Hello {attendance.student.username},\n\n"
                    f"Your attendance for "
                    f"{attendance.attendance_date} "
                    f"has been approved by the administrator.\n\n"
                    "Your attendance status is now APPROVED.\n\n"
                    "Regards,\n"
                    "Student Facial Attendance System"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student_email],
                fail_silently=False,
            )

            if email_sent == 1:
                print(
                    f"APPROVAL EMAIL SENT SUCCESSFULLY TO: "
                    f"{student_email}"
                )
            else:
                print(
                    f"EMAIL NOT SENT TO: {student_email}"
                )

        except Exception as e:
            print(
                "EMAIL SENDING ERROR:",
                repr(e)
            )

    return redirect("attendance_approvals")


# =========================================================
# ADMIN: REJECT ATTENDANCE
# =========================================================

@login_required
@require_POST
def reject_attendance(request, attendance_id):
    if request.user.role not in ["ADMIN", "SUPERADMIN"]:
        return redirect("home")

    attendance = get_object_or_404(
        Attendance,
        id=attendance_id
    )

    if attendance.status == "PENDING":
        attendance.status = "REJECTED"

        attendance.save(
            update_fields=["status"]
        )

    return redirect("attendance_approvals")