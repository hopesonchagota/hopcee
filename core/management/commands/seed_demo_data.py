from django.core.management.base import BaseCommand

from catalog.models import Category, Market, Product
from core.models import Testimonial


class Command(BaseCommand):
    help = "Seed Hopcee with demo markets, categories, products and testimonials."

    def handle(self, *args, **options):
        mitundu, _ = Market.objects.update_or_create(
            name="Mitundu Market",
            defaults={
                "description": "A vibrant farm-produce market a short drive from LUANAR Bunda Campus — our main source for fresh Irish Potato, Soya and Bonya.",
                "image_url": "/static/img/placeholders/market-mitundu.svg",
                "typical_transport_fee": 12000,
                "is_active": True,
            },
        )
        town, _ = Market.objects.update_or_create(
            name="Town",
            defaults={
                "description": "Lilongwe town shops and hardware stores — great for Electrical Equipment, Mafuta and packaged goods.",
                "image_url": "/static/img/placeholders/market-town.svg",
                "typical_transport_fee": 18000,
                "is_active": True,
            },
        )

        categories_data = [
            ("Irish Potato", "potato", "/static/img/placeholders/potato.svg"),
            ("Electrical Equipment", "bolt", "/static/img/placeholders/electrical.svg"),
            ("Soya Pieces / Thumba", "soya", "/static/img/placeholders/soya.svg"),
            ("Mafuta (Cooking Oil)", "oil", "/static/img/placeholders/oil.svg"),
            ("Bonya Small Fish", "fish", "/static/img/placeholders/fish.svg"),
            ("Many Others", "basket", "/static/img/placeholders/basket.svg"),
        ]
        categories = {}
        for order, (name, icon, img) in enumerate(categories_data):
            cat, _ = Category.objects.update_or_create(
                name=name, defaults={"icon": icon, "image_url": img, "order": order, "is_active": True}
            )
            categories[name] = cat

        products_data = [
            ("Irish Potato (Grade A)", "Irish Potato", mitundu, "bag_50kg", 45000, "/static/img/placeholders/potato.svg"),
            ("Irish Potato (Loose)", "Irish Potato", mitundu, "kg", 950, "/static/img/placeholders/potato.svg"),
            ("Extension Cable (5m)", "Electrical Equipment", town, "piece", 8500, "/static/img/placeholders/electrical.svg"),
            ("LED Bulb 12W", "Electrical Equipment", town, "piece", 3200, "/static/img/placeholders/electrical.svg"),
            ("Soya Pieces (Thumba)", "Soya Pieces / Thumba", mitundu, "kg", 2600, "/static/img/placeholders/soya.svg"),
            ("Cooking Oil (Mafuta) 2L", "Mafuta (Cooking Oil)", town, "litre", 6800, "/static/img/placeholders/oil.svg"),
            ("Bonya Dried Fish", "Bonya Small Fish", mitundu, "kg", 5200, "/static/img/placeholders/fish.svg"),
            ("Rice (Local) 5kg", "Many Others", mitundu, "bucket", 9500, "/static/img/placeholders/basket.svg"),
        ]
        for name, cat_name, market, unit, price, img in products_data:
            Product.objects.update_or_create(
                name=name,
                market=market,
                defaults={
                    "category": categories[cat_name],
                    "unit": unit,
                    "ordering_price": price,
                    "image_url": img,
                    "is_available": True,
                },
            )

        testimonials_data = [
            ("Chikondi Banda", "BSc Agribusiness Mgmt", 5, "Hopcee saved me a trip to Mitundu — my potatoes arrived right at my hostel, at the real market price!"),
            ("Thandiwe Phiri", "BSc Food Science", 5, "I love that I only pay half the transport. Delivery was on time and the WhatsApp updates kept me calm."),
            ("Blessings Kaunda", "BSc Horticulture", 4, "Ordered electrical equipment for my project and it arrived faster than I expected. Very reliable."),
        ]
        for name, prog, rating, quote in testimonials_data:
            Testimonial.objects.update_or_create(
                student_name=name,
                defaults={
                    "programme": prog,
                    "rating": rating,
                    "quote": quote,
                                        "is_published": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("Demo data seeded: 2 markets, 6 categories, 8 products, 3 testimonials."))
