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
    products_qs = Product.objects.filter(is_available=True).select_related("category", "market")

    category_slug = request.GET.get("category")
    market_slug = request.GET.get("market")
    query = request.GET.get("q")

    if category_slug:
        products_qs = products_qs.filter(category__slug=category_slug)
    if market_slug:
        products_qs = products_qs.filter(market__slug=market_slug)
    if query:
        products_qs = products_qs.filter(name__icontains=query)

    context = {
        "products": products_qs,
        "categories": Category.objects.filter(is_active=True),
        "markets": Market.objects.filter(is_active=True),
        "selected_category": category_slug,
        "selected_market": market_slug,
        "query": query or "",
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
