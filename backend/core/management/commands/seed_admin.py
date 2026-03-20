from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update the default admin user."

    def handle(self, *args, **options):
        User = get_user_model()

        username = "admin"
        email = "admin@kitchenmanager.local"
        password = "admin123"

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS("Admin user created successfully."))
        else:
            user.email = email
            user.role = "admin"
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS("Admin user updated successfully."))