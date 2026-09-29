import re

from django import forms
from django.core.exceptions import ValidationError

from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer_name", "delivery_date", "delivery_phone", "delivery_point", "notes"]
        labels = {
            "customer_name": "Your Name",
            "delivery_date": "Preferred Delivery Date",
            "delivery_phone": "Your WhatsApp Number",
            "delivery_point": "Delivery Point at Bunda Campus",
            "notes": "Additional Notes (optional)",
        }
        widgets = {
            "delivery_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " form-input").strip()
        self.fields["customer_name"].widget.attrs["placeholder"] = "e.g. Chikondi Banda"
        self.fields["delivery_phone"].widget.attrs["placeholder"] = "e.g. 0991234567"
        self.fields["delivery_phone"].required = True
        self.fields["delivery_phone"].help_text = (
            "Required — this is the number Hopcee will WhatsApp you on to confirm your order."
        )

    def clean_delivery_phone(self):
        phone = self.cleaned_data["delivery_phone"].strip()
        digits = re.sub(r"\D", "", phone)
        if len(digits) < 9:
            raise ValidationError("Please enter a valid WhatsApp phone number.")
        return phone


class OrderTrackingForm(forms.Form):
    order_code = forms.CharField(
        max_length=12,
        label="Order Code",
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "e.g. HPC-A1B2C3D4"}),
    )
    phone_number = forms.CharField(
        max_length=20,
        label="Phone Number used on the order",
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "e.g. 0991234567"}),
    )
