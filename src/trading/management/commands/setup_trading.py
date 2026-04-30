from celery.bin.control import status
from celery.schedules import schedule
from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule

 # python manage.py setup_trading


class Command(BaseCommand):
    help = 'Sets up periodic tasks for trading operations'

    def handle(self, *args, **options):

        tasks_data = [
            {'name': 'Buy Apples', 'task': 'trading.tasks.buy_apple', 'seconds': 6},
            {'name': 'Buy Bananas', 'task': 'trading.tasks.buy_banana', 'seconds': 9},
            {'name': 'Buy Peaches', 'task': 'trading.tasks.buy_peach', 'seconds': 12},
            {'name': 'Buy Pineapples', 'task': 'trading.tasks.buy_pineapple', 'seconds': 15},

            {'name': 'Sell Apples', 'task': 'trading.tasks.sell_apple', 'seconds': 15},
            {'name': 'Sell Bananas', 'task': 'trading.tasks.sell_banana', 'seconds': 12},
            {'name': 'Sell Peaches', 'task': 'trading.tasks.sell_peach', 'seconds': 9},
            {'name': 'Sell Pineapples', 'task': 'trading.tasks.sell_pineapple', 'seconds': 6},

        ]
        self.stdout.write(self.style.SUCCESS('Setting up periodic tasks...'))

        for item in tasks_data:
            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=item['seconds'],
                period=IntervalSchedule.SECONDS,
            )
            task, created = PeriodicTask.objects.update_or_create(
                name=item['name'],
                defaults={
                    'task': item['task'],
                    'interval': schedule,
                    'queue': 'queue1',
                    "enabled": True,
                }
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'- {item["name"]}: {status}')

        self.stdout.write(self.style.SUCCESS('Всі завдання успішно налаштовані!'))