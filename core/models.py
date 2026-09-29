from django.db import models


class Testimonial(models.Model):
    student_name = models.CharField(max_length=120)
    programme = models.CharField(max_length=120, blank=True)
    photo_url = models.URLField(blank=True)
    quote = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5, help_text="1 to 5 stars")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student_name} ({self.rating}★)"


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    phone_number = models.CharField(max_length=20)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.created_at:%d %b %Y}"
