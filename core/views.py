from django.contrib import messages
from django.shortcuts import redirect, render

from catalog.models import Category, Market, Product

from .models import ContactMessage, Testimonial


def home(request):
    context = {
        "markets": Market.objects.filter(is_active=True),
        "categories": Category.objects.filter(is_active=True),
        "testimonials": Testimonial.objects.filter(is_published=True)[:6],
        "featured_products": Product.objects.filter(is_available=True).select_related(
            "category", "market"
        )[:8],
    }
    return render(request, "core/home.html", context)


def products(request):
    """Advertisement page: shows everything, no filtering.

    ?market= and ?category= (from links on the home page) only pre-fill
    the WhatsApp request form.
    """
    products_qs = Product.objects.filter(is_available=True).select_related("category", "market")

    market = Market.objects.filter(slug=request.GET.get("market")).first()
    category = Category.objects.filter(slug=request.GET.get("category")).first()

    context = {
        "products": products_qs,
        "categories": Category.objects.filter(is_active=True),
        "markets": Market.objects.filter(is_active=True),
        "prefill_market": market.name if market else "",
        "prefill_category": category.name if category else "",
    }
    return render(request, "core/products.html", context)


def about(request):
    return render(request, "core/about.html")


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        message = request.POST.get("message", "").strip()
        if name and phone_number and message:
            ContactMessage.objects.create(name=name, phone_number=phone_number, message=message)
            messages.success(request, "Thanks! We received your message and will WhatsApp you back soon.")
            return redirect("core:contact")
        messages.error(request, "Please fill in your name, phone number and message.")
    return render(request, "core/contact.html")
