import uuid

from django.conf import settings
from django.db import models

from catalog.models import Market, Product


# ---------------------------------------------------------------------------
# Cart (one open cart per browser session — no login required)
# ---------------------------------------------------------------------------
class Cart(models.Model):
    session_key = models.CharField(max_length=40, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.session_key[:8]}…"

    @property
    def items_total(self):
        return sum((item.subtotal for item in self.items.all()), start=0)

    @property
    def markets_in_cart(self):
        return Market.objects.filter(products__cart_items__cart=self).distinct()

    @property
    def is_empty(self):
        return not self.items.exists()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return self.product.ordering_price * self.quantity


# ---------------------------------------------------------------------------
# Orders — placed by guests (no account needed). The customer is identified
# only by the name and WhatsApp number they type in at checkout.
# ---------------------------------------------------------------------------
class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_BOUGHT = "bought"
    STATUS_IN_TRANSIT = "in_transit"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_BOUGHT, "Bought"),
        (STATUS_IN_TRANSIT, "In Transit"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    order_code = models.CharField(max_length=12, unique=True, editable=False, blank=True)

    # Optional: only ever set by staff in Admin if they want to link an order
    # to a registered account. Never required at checkout.
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
    )
    customer_name = models.CharField(max_length=150, help_text="Name given by the customer at checkout")

    market = models.ForeignKey(Market, on_delete=models.PROTECT, related_name="orders")

    delivery_date = models.DateField()
    delivery_phone = models.CharField(
        max_length=20, help_text="Customer's WhatsApp number — required to complete the order"
    )
    delivery_point = models.CharField(
        max_length=150, default="LUANAR Bunda Campus", help_text="Drop-off point on campus"
    )
    notes = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    # Internal-only figures — never rendered on any customer-facing page.
    # Kept for Hopcee's own record-keeping and Admin reporting.
    goods_subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transport_fee_half = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    whatsapp_message_sent = models.BooleanField(
        default=False, help_text="Marked true once the customer has been redirected to WhatsApp with this order's text."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.order_code} — {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.order_code:
            self.order_code = f"HPC-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def recalculate_totals(self, commit=True):
        """Ordering price total + half of the market's transport fee. Internal use only."""
        subtotal = sum((item.subtotal for item in self.items.all()), start=0)
        half_transport = self.market.half_transport_fee if self.market_id else 0
        self.goods_subtotal = subtotal
        self.transport_fee_half = half_transport
        self.total_amount = subtotal + half_transport
        if commit:
            self.save(update_fields=["goods_subtotal", "transport_fee_half", "total_amount"])

    @property
    def status_steps(self):
        """Ordered list of (status, label, is_reached, is_current) for the tracker UI."""
        order_flow = [self.STATUS_PENDING, self.STATUS_BOUGHT, self.STATUS_IN_TRANSIT, self.STATUS_DELIVERED]
        current_index = order_flow.index(self.status) if self.status in order_flow else -1
        steps = []
        for idx, code in enumerate(order_flow):
            label = dict(self.STATUS_CHOICES)[code]
            steps.append(
                {
                    "code": code,
                    "label": label,
                    "reached": current_index >= idx,
                    "current": current_index == idx,
                }
            )
        return steps


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    product_name = models.CharField(max_length=150)  # snapshot in case product changes later
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        if not self.product_name:
            self.product_name = self.product.name
        if not self.unit_price:
            self.unit_price = self.product.ordering_price
        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_history")
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["changed_at"]
        verbose_name_plural = "Order status history"

    def __str__(self):
        return f"{self.order.order_code} -> {self.status}"


# ---------------------------------------------------------------------------
# "Your Money is Safe" ledger — every kwacha in/out of an order, visible to
# staff in the admin for full transparency on the trust guarantee.
# ---------------------------------------------------------------------------
class MoneyLedgerEntry(models.Model):
    ENTRY_COLLECTED = "collected"
    ENTRY_PAID_MARKET = "paid_market"
    ENTRY_PAID_TRANSPORT = "paid_transport"
    ENTRY_REFUND = "refund"

    ENTRY_CHOICES = [
        (ENTRY_COLLECTED, "Collected from Student"),
        (ENTRY_PAID_MARKET, "Paid to Market Vendor"),
        (ENTRY_PAID_TRANSPORT, "Paid for Transport"),
        (ENTRY_REFUND, "Refunded to Student"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="ledger_entries")
    entry_type = models.CharField(max_length=20, choices=ENTRY_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Money-Safe Ledger Entry"
        verbose_name_plural = "Money-Safe Ledger"

    def __str__(self):
        return f"{self.get_entry_type_display()}: MWK {self.amount} ({self.order.order_code})"


# ---------------------------------------------------------------------------
# Testimonials & WhatsApp notification log
# ---------------------------------------------------------------------------
class WhatsAppNotificationLog(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="whatsapp_logs", null=True, blank=True
    )
    to_number = models.CharField(max_length=20)
    message = models.TextField()
    was_sent_via_api = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"WhatsApp to {self.to_number} @ {self.created_at:%Y-%m-%d %H:%M}"
