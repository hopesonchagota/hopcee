from django.contrib import admin

from .models import ContactMessage, Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("student_name", "programme", "rating", "is_published", "created_at")
    list_editable = ("is_published",)
    list_filter = ("is_published", "rating")
    search_fields = ("student_name", "quote")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "phone_number", "is_resolved", "created_at")
    list_editable = ("is_resolved",)
    list_filter = ("is_resolved",)
    search_fields = ("name", "phone_number", "message")
