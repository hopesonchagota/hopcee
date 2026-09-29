from django.conf import settings


def site_settings(request):
    return {
        "HOPCEE": settings.HOPCEE,
        "GOOGLE_SITE_VERIFICATION": settings.GOOGLE_SITE_VERIFICATION,
        "cart_count": getattr(request, "cart_count", 0),
    }
