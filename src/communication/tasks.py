import requests
from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from communication.models import Message, Joke
from django.utils import timezone


def _get_joke_text() -> str:
    try:
        r = requests.get(
            'https://v2.jokeapi.dev/joke/Any?lang=ru&type=twopart',
            timeout=5
        )
        data = r.json()
        if not data.get('error') and data.get('type') == 'twopart':
            return f"{data['setup']} — {data['delivery']}"
        raise ValueError
    except Exception:
        # fallback — английский
        r = requests.get(
            'https://v2.jokeapi.dev/joke/Any?type=twopart',
            timeout=5
        )
        data = r.json()
        if data.get('type') == 'twopart':
            return f"{data['setup']} — {data['delivery']}"
        return data.get('joke', 'Шутник устал шутить...')


@shared_task(bind=True, queue='joke_queue')
def broadcast_joke(self):
    # Берём случайный жарт из БД, если есть — не дёргаем API
    joke = Joke.objects.order_by('?').first()

    if joke:
        text = joke.content
    else:
        text = _get_joke_text()
        Joke.objects.get_or_create(content=text)  # unique=True защищает от дублей

    Message.objects.create(sender='Шутник', content=text, user=None)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)('chat', {
        'type': 'chat_message',
        'message': text,
        'username': 'Шутник',
        'time': timezone.now().strftime('%H:%M'),
    })

    # Следующий жарт через N секунд = кол-во символов текущего
    broadcast_joke.apply_async(countdown=max(len(text), 10), queue='joke_queue')


@shared_task(queue='joke_queue')
def populate_jokes(count: int = 50):
    """Наполняет БД жартами. Запускать один раз или по crontab."""
    added = 0
    errors = 0

    while added < count and errors < 5:
        try:
            r = requests.get(
                'https://v2.jokeapi.dev/joke/Any?type=twopart&amount=10',
                timeout=5
            )
            for item in r.json().get('jokes', [r.json()]):
                if item.get('type') == 'twopart':
                    text = f"{item['setup']} — {item['delivery']}"
                elif item.get('joke'):
                    text = item['joke']
                else:
                    continue
                _, created = Joke.objects.get_or_create(content=text)
                if created:
                    added += 1
        except Exception:
            errors += 1

    return f"Добавлено: {added}, ошибок: {errors}"