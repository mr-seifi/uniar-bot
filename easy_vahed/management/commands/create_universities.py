from django.core.management.base import BaseCommand
from easy_vahed.enums import UniversityChoices
from easy_vahed.models import University


class Command(BaseCommand):
    help = 'This command creates universities from enums'

    def handle(self, *args, **options):
        for name in UniversityChoices.names:
            University.objects.create(name=name)
        self.stdout.write('Universities created!')
