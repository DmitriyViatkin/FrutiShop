from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Sets up periodic tasks, users and inventory for trading operations'

    def handle(self, *args, **options):
        # ── Периодические задачи ──────────────────────────────
        tasks_data = [
            {'name': 'Buy Apples',       'task': 'trading.tasks.buy_apple',      'seconds': 6},
            {'name': 'Buy Bananas',      'task': 'trading.tasks.buy_banana',     'seconds': 9},
            {'name': 'Buy Peaches',      'task': 'trading.tasks.buy_peach',      'seconds': 12},
            {'name': 'Buy Pineapples',   'task': 'trading.tasks.buy_pineapple',  'seconds': 15},
            {'name': 'Sell Apples',      'task': 'trading.tasks.sell_apple',     'seconds': 15},
            {'name': 'Sell Bananas',     'task': 'trading.tasks.sell_banana',    'seconds': 12},
            {'name': 'Sell Peaches',     'task': 'trading.tasks.sell_peach',     'seconds': 9},
            {'name': 'Sell Pineapples',  'task': 'trading.tasks.sell_pineapple', 'seconds': 6},
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
                    'queue': 'queue_1',
                    'enabled': True,
                }
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  - {item["name"]}: {status}')

        # ── Суперюзеры ────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS('\nSetting up superusers...'))
        superusers = [
            {'username': 'admin',  'password': 'admin123',  'email': 'admin@fruit.shop'},
            {'username': 'admin2', 'password': 'admin1234', 'email': 'admin2@fruit.shop'},
        ]
        for su in superusers:
            user, created = User.objects.get_or_create(username=su['username'])
            if created:
                user.set_password(su['password'])
                user.email = su['email']
                user.is_staff = True
                user.is_superuser = True
                user.save()
                self.stdout.write(f'  - Superuser "{su["username"]}": Created')
            else:
                self.stdout.write(f'  - Superuser "{su["username"]}": Already exists')

        # ── Обычные пользователи ──────────────────────────────
        self.stdout.write(self.style.SUCCESS('\nSetting up regular users...'))
        regular_users = [
            {'username': 'trader1', 'password': 'pass1234', 'email': 'trader1@fruit.shop'},
            {'username': 'trader2', 'password': 'pass1234', 'email': 'trader2@fruit.shop'},
            {'username': 'trader3', 'password': 'pass1234', 'email': 'trader3@fruit.shop'},
        ]
        for u in regular_users:
            user, created = User.objects.get_or_create(username=u['username'])
            if created:
                user.set_password(u['password'])
                user.email = u['email']
                user.save()
                self.stdout.write(f'  - User "{u["username"]}": Created')
            else:
                self.stdout.write(f'  - User "{u["username"]}": Already exists')

        # ── Инвентарь фруктов ─────────────────────────────────
        self.stdout.write(self.style.SUCCESS('\nSetting up inventory...'))
        from trading.models import Inventory, Account

        fruits = [
            {'fruit': 'apple',     'quantity': 10},
            {'fruit': 'banana',    'quantity': 10},
            {'fruit': 'pineapple', 'quantity': 10},
            {'fruit': 'peach',     'quantity': 10},
        ]
        for f in fruits:
            inv, created = Inventory.objects.get_or_create(
                fruit=f['fruit'],
                defaults={'quantity': f['quantity']}
            )
            if not created:
                inv.quantity = f['quantity']
                inv.save()
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  - {f["fruit"].capitalize()} x{f["quantity"]}: {status}')

        # ── Счёт ──────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS('\nSetting up account...'))
        account, created = Account.objects.get_or_create(
            pk=2,
            defaults={'balance': 10000}
        )
        if not created:
            self.stdout.write(f'  - Account pk=2 already exists, balance: ${account.balance}')
        else:
            self.stdout.write(f'  - Account pk=2 created with balance: $10000')

        self.stdout.write(self.style.SUCCESS('\n✅ Всі завдання успішно налаштовані!'))