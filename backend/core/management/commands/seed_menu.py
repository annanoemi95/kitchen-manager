from django.core.management.base import BaseCommand
from core.models import Category, Dish

class Command(BaseCommand):
    help = "Popola il database con categorie e piatti iniziali (Fake Data)"

    def handle(self, *args, **options):
        # 1. Creazione Categorie
        cat_pizza, _ = Category.objects.get_or_create(name="Pizze")
        cat_burger, _ = Category.objects.get_or_create(name="Burger")
        cat_drink, _ = Category.objects.get_or_create(name="Bevande")

        # 2. Lista piatti da creare
        dishes = [
            {
                "name": "Margherita",
                "description": "Pomodoro, mozzarella, basilico fresco",
                "price": 8.50,
                "category": cat_pizza,
                "is_active": True,
                "is_available": True
            },
            {
                "name": "Diavola",
                "description": "Pomodoro, mozzarella, salame piccante",
                "price": 10.00,
                "category": cat_pizza,
                "is_active": True,
                "is_available": True # Visibile e ordinabile
            },
            {
                "name": "Bacon Burger",
                "description": "Manzo 200g, cheddar, bacon croccante",
                "price": 12.00,
                "category": cat_burger,
                "is_active": True,
                "is_available": False  # Visibile ma sold out
            },

            {
                "name": "Pizza Storica 2025",
                "description": "Edizione limitata dello scorso anno",
                "price": 15.00,
                "category": cat_pizza,
                "is_active": False,
                "is_available": False  # Soft Delete: Nascosta dal menu ma presente nel DB
            },
            {
                "name": "Coca Cola 33cl",
                "description": "Lattina",
                "price": 2.50,
                "category": cat_drink,
                "is_active": True,
                "is_available": True
            }
        ]

        # 3. Ciclo di creazione dei piatti
        for data in dishes:
            dish, created = Dish.objects.update_or_create(
                name=data["name"],
                defaults=data
            )
            status = "creato" if created else "aggiornato"
            self.stdout.write(self.style.SUCCESS(f"Piatto '{dish.name}' {status}."))

        self.stdout.write(self.style.SUCCESS("Seed del menu completato!"))