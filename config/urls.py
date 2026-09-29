from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("orders/", include("orders.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Hopcee Bulk Ordering Service — Admin"
admin.site.site_title = "Hopcee Admin"
admin.site.index_title = "Manage markets, products, orders & the money-safe ledger"
