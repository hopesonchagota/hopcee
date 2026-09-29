from django.db import models
from django.utils.text import slugify


class Market(models.Model):
    """A sourcing location Hopcee travels to, e.g. Mitundu Market or Town."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    description = models.TextField(
        blank=True, help_text="Short blurb shown in the 'Our Markets' section."
    )
    image_url = models.URLField(
        blank=True, help_text="Photo shown on the homepage for this market."
    )
    typical_transport_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Round-trip transport cost Hopcee usually pays to reach this market (MWK).",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def half_transport_fee(self):
        return self.typical_transport_fee / 2


class Category(models.Model):
    """Product category, e.g. Irish Potato, Electrical Equipment, Thumba, Mafuta, Bonya."""

    ICON_CHOICES = [
        ("potato", "Irish Potato"),
        ("bolt", "Electrical Equipment"),
        ("soya", "Soya Pieces / Thumba"),
        ("oil", "Mafuta (Cooking Oil)"),
        ("fish", "Bonya Small Fish"),
        ("basket", "Many Others"),
    ]

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    icon = models.CharField(max_length=20, choices=ICON_CHOICES, default="basket")
    description = models.CharField(max_length=255, blank=True)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    UNIT_CHOICES = [
        ("kg", "Kilogram (kg)"),
        ("bag_50kg", "50kg Bag"),
        ("bag_90kg", "90kg Bag"),
        ("piece", "Piece"),
        ("litre", "Litre"),
        ("pack", "Pack"),
        ("box", "Box"),
        ("bucket", "Bucket"),
    ]

    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default="kg")
    ordering_price = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="The buying price at the market (MWK) per unit."
    )
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category__order", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_unit_display()}) — {self.market.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.market.name}")
            self.slug = base_slug
        super().save(*args, **kwargs)
