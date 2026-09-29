from django.contrib import admin

from .models import Category, Market, Product


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ("name", "typical_transport_fee", "half_transport_fee", "is_active")
    list_editable = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "order", "is_active")
    list_editable = ("order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "market", "unit", "ordering_price", "is_available")
    list_filter = ("category", "market", "is_available")
    list_editable = ("ordering_price", "is_available")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("market", "category")
