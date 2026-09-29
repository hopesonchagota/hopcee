from django.db import migrations
from django.utils.text import slugify

MARKETS = [
    (
        "Mitundu Market",
        "A busy farm-produce market near LUANAR Bunda Campus. Great for Irish potato, soya, bonya, rice and beans.",
        "/static/img/placeholders/market-mitundu.svg",
    ),
    (
        "Town",
        "Lilongwe town shops and hardware stores. Great for electrical equipment, cooking oil and packaged goods.",
        "/static/img/placeholders/market-town.svg",
    ),
]

CATEGORIES = [
    ("Irish Potato", "potato", "/static/img/placeholders/potato.svg"),
    ("Bonya Small Fish", "fish", "/static/img/placeholders/fish.svg"),
    ("Electrical Equipment", "bolt", "/static/img/placeholders/electrical.svg"),
    ("Rice", "basket", "/static/img/placeholders/basket.svg"),
    ("Beans", "basket", "/static/img/placeholders/basket.svg"),
    ("Soya Pieces / Thumba", "soya", "/static/img/placeholders/soya.svg"),
    ("Mafuta (Cooking Oil)", "oil", "/static/img/placeholders/oil.svg"),
    ("Many Others", "basket", "/static/img/placeholders/basket.svg"),
]


def add_defaults(apps, schema_editor):
    Market = apps.get_model("catalog", "Market")
    Category = apps.get_model("catalog", "Category")

    for name, description, image in MARKETS:
        Market.objects.get_or_create(
            name=name,
            defaults={
                "slug": slugify(name),
                "description": description,
                "image_url": image,
                "is_active": True,
            },
        )

    for order, (name, icon, image) in enumerate(CATEGORIES):
        Category.objects.get_or_create(
            name=name,
            defaults={
                "slug": slugify(name),
                "icon": icon,
                "image_url": image,
                "order": order,
                "is_active": True,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        # Reverse is a no-op so rolling back never deletes markets you edited.
        migrations.RunPython(add_defaults, migrations.RunPython.noop),
    ]
