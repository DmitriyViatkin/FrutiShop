import requests
from channels.layers import get_channel_layer
from celery import shared_task, current_app
from asgiref.sync import async_to_sync
from communication.models import Message, Joke
from django.utils import timezone



def get_joke():

    r= requests.get('https://v2.jokeapi.dev/joke/Any?lang=ru&type=twopart')

    data= r.json()
    if data['type'] == 'twopart':
        return f"{data['setup']} - {data['delivery']}"
    return data['joke']

@shared_task(bind=True, queue="joke_queue")
def fetch_joke(self):

    text = get_joke()
    Joke.objects.create(content=text)

    Message.objects.create(sender='JokeAPI', content=text, user=None)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)('chat', {
        'type': 'chat_message',
        'message': text,
        'username': 'Шутник',
        'time': timezone.now().strftime('%H:%M')
    })
    fetch_joke.apply_async(countdown=len(text), queue="joke_queue")