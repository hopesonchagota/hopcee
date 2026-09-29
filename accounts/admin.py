from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class HopceeUserAdmin(UserAdmin):
    list_display = (
        "username",
        "get_full_name",
        "student_number",
        "phone_number",
        "residence",
        "is_student_verified",
        "is_staff",
    )
    list_filter = ("residence", "is_student_verified", "is_staff", "is_active")
    search_fields = ("username", "first_name", "last_name", "student_number", "phone_number", "email")
    list_editable = ("is_student_verified",)

    fieldsets = UserAdmin.fieldsets + (
        (
            "Hopcee Student Details",
            {
                "fields": (
                    "student_number",
                    "phone_number",
                    "programme",
                    "year_of_study",
                    "residence",
                    "hostel_name",
                    "is_student_verified",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Hopcee Student Details",
            {"fields": ("student_number", "phone_number", "programme", "residence")},
        ),
    )

    @admin.display(description="Full name")
    def get_full_name(self, obj):
        return obj.get_full_name() or "—"
