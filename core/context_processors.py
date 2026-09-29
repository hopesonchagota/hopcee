from django.conf import settings


def site_settings(request):
    return {
        "HOPCEE": settings.HOPCEE,
        "cart_count": getattr(request, "cart_count", 0),
    }
