from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

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
    """Categories page: customers only see categories, then chat on WhatsApp.

    ?market= and ?category= (from links on the home page) only pre-fill
    the WhatsApp request form.
    """
    market = Market.objects.filter(slug=request.GET.get("market")).first()
    category = Category.objects.filter(slug=request.GET.get("category")).first()

    context = {
        "categories": Category.objects.filter(is_active=True),
        "markets": Market.objects.filter(is_active=True),
        "prefill_market": market.name if market else "",
        "prefill_category": category.name if category else "",
    }
    return render(request, "core/products.html", context)


def robots_txt(request):
    sitemap_url = request.build_absolute_uri(reverse("core:sitemap"))
    body = f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /orders/\n\nSitemap: {sitemap_url}\n"
    return HttpResponse(body, content_type="text/plain")


def sitemap_xml(request):
    pages = ["core:home", "core:products", "core:about", "core:contact"]
    urls = "".join(
        f"<url><loc>{request.build_absolute_uri(reverse(name))}</loc></url>" for name in pages
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + "</urlset>"
    )
    return HttpResponse(xml, content_type="application/xml")


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
