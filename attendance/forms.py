from django import forms
from .models import Attendance

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = []
        
class FaceVerificationForm(forms.Form):
    face_image = forms.ImageField()