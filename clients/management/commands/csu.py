from django.core.management import BaseCommand

from clients.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create(
            email='admin@andrey.pro',
            first_name='Admin',
            last_name='Andrey',
            is_staff=True,
            is_superuser=True
        )

        user.set_password('123qwe321')
        user.save()
