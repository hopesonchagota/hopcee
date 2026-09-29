from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model for Hopcee students (and staff/admin).

    Extends Django's AbstractUser so we keep all the battle-tested auth
    machinery (password hashing, permissions, admin integration) while
    adding the fields Hopcee actually needs from a LUANAR student.
    """

    HOSTEL_CHOICES = [
        ("on_campus", "On-Campus Hostel"),
        ("off_campus", "Off-Campus / Private Hostel"),
    ]

    student_number = models.CharField(max_length=30, unique=True)
    phone_number = models.CharField(
        max_length=20, help_text="WhatsApp-reachable phone number, e.g. 0991234567"
    )
    programme = models.CharField(max_length=120, blank=True, help_text="e.g. BSc Agribusiness")
    year_of_study = models.PositiveSmallIntegerField(null=True, blank=True)
    residence = models.CharField(max_length=20, choices=HOSTEL_CHOICES, default="on_campus")
    hostel_name = models.CharField(max_length=120, blank=True)
    is_student_verified = models.BooleanField(
        default=False, help_text="Staff can tick this once student ID has been confirmed."
    )
    date_joined_hopcee = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        full = self.get_full_name()
        return f"{full} ({self.student_number})" if full else self.username
