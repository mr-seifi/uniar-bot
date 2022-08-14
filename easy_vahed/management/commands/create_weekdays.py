from django.core.management.base import BaseCommand
from easy_vahed.models import WeekDay


class Command(BaseCommand):
    help = 'This command helps you create weekdays easily!'

    def handle(self, *args, **options):
        for i in range(0, 7):
            WeekDay.objects.create(day=i)
        self.stdout.write('Weekdays created!')
