from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class StudentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "student_number",
            "phone_number",
            "programme",
            "year_of_study",
            "residence",
            "hostel_name",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "username": "Choose a username",
            "student_number": "e.g. BUN-21-045",
            "phone_number": "e.g. 0991234567 (WhatsApp)",
            "programme": "e.g. BSc Agribusiness Management",
            "year_of_study": "1 - 5",
            "hostel_name": "e.g. Chirunga Hostel",
        }
        for field_name, placeholder in placeholders.items():
            self.fields[field_name].widget.attrs["placeholder"] = placeholder
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " form-input").strip()


class StudentLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " form-input").strip()


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "programme",
            "year_of_study",
            "residence",
            "hostel_name",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " form-input").strip()
