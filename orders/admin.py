from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Cart,
    CartItem,
    MoneyLedgerEntry,
    Order,
    OrderItem,
    OrderStatusHistory,
    WhatsAppNotificationLog,
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("subtotal_display",)
    fields = ("product", "product_name", "unit_price", "quantity", "subtotal_display")

    @admin.display(description="Subtotal")
    def subtotal_display(self, obj):
        return f"MWK {obj.subtotal:,.0f}" if obj.pk else "—"


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ("status", "changed_at", "changed_by", "note")
    can_delete = False


class MoneyLedgerEntryInline(admin.TabularInline):
    model = MoneyLedgerEntry
    extra = 0
    fields = ("entry_type", "amount", "note", "recorded_by", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_code",
        "customer_name",
        "delivery_phone",
        "market",
        "status_badge",
        "total_amount",
        "delivery_date",
        "created_at",
    )
    list_filter = ("status", "market", "delivery_date")
    search_fields = ("order_code", "customer_name", "delivery_phone")
    readonly_fields = ("order_code", "goods_subtotal", "transport_fee_half", "total_amount", "created_at", "updated_at")
    inlines = [OrderItemInline, OrderStatusHistoryInline, MoneyLedgerEntryInline]
    autocomplete_fields = ("market",)
    actions = ["mark_bought", "mark_in_transit", "mark_delivered"]

    fieldsets = (
        ("Order", {"fields": ("order_code", "customer_name", "customer", "market", "status")}),
        ("Delivery", {"fields": ("delivery_date", "delivery_phone", "delivery_point", "notes")}),
        ("Totals (auto-calculated)", {"fields": ("goods_subtotal", "transport_fee_half", "total_amount")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Status")
    def status_badge(self, obj):
        colors = {
            "pending": "#f59e0b",
            "bought": "#3b82f6",
            "in_transit": "#8b5cf6",
            "delivered": "#10b981",
            "cancelled": "#ef4444",
        }
        color = colors.get(obj.status, "#6b7280")
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:9999px;font-size:12px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.recalculate_totals()

    def _bulk_set_status(self, request, queryset, status):
        for order in queryset:
            order.status = status
            order.save()

    @admin.action(description="Mark selected orders as Bought")
    def mark_bought(self, request, queryset):
        self._bulk_set_status(request, queryset, Order.STATUS_BOUGHT)

    @admin.action(description="Mark selected orders as In Transit")
    def mark_in_transit(self, request, queryset):
        self._bulk_set_status(request, queryset, Order.STATUS_IN_TRANSIT)

    @admin.action(description="Mark selected orders as Delivered")
    def mark_delivered(self, request, queryset):
        self._bulk_set_status(request, queryset, Order.STATUS_DELIVERED)


@admin.register(MoneyLedgerEntry)
class MoneyLedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("order", "entry_type", "amount", "recorded_by", "created_at")
    list_filter = ("entry_type",)
    search_fields = ("order__order_code",)


@admin.register(WhatsAppNotificationLog)
class WhatsAppNotificationLogAdmin(admin.ModelAdmin):
    list_display = ("to_number", "order", "was_sent_via_api", "created_at")
    readonly_fields = ("order", "to_number", "message", "was_sent_via_api", "created_at")
    list_filter = ("was_sent_via_api",)

    def has_add_permission(self, request):
        return False


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("session_key", "updated_at")
    inlines = [CartItemInline]
    search_fields = ("session_key",)
