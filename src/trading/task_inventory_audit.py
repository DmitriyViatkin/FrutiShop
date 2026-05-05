import time
from asyncio import timeout

from asgiref.sync import async_to_sync
from celery import shared_task, current_app
from channels.layers import get_channel_layer
from django.core.cache import cache




@shared_task(bind=True, queue="audit_queue")
def inventory_audit(self, user_id):

    lock_key = "audit_lock"

    if not cache.add ( lock_key, 'true', 6):
        return {"status":"already_running", "user_id": user_id }

    try:
        current_app.control.cancel_consumer("queue_1")
        start_time = time.time()

        # Імітація тривалої перевірки
        while time.time() - start_time < 5:
            _ = [x**2 for x in range(1000000)]
        return {"status": "completed", "user_id": user_id}
    finally:
        current_app.control.add_consumer("queue_1")
        cache.delete(lock_key)

@shared_task(bind=True, queue="audit_queue")
def bank_audit(self, user_id):

    lock_key = "audit_lock"



    channel_layer= get_channel_layer()

    def send_progress(progress, message=''):
        async_to_sync(channel_layer.group_send)('fruit_trading', {
            'type': 'audit_progress',
            'progress': progress,
            'message': message
        })
    try:
        current_app.control.cancel_consumer("queue_1")
        start_time = time.time()


        while time.time() - start_time < 15:
            progress = int((time.time() - start_time) / 15 * 100)


            send_progress(progress)

            self.update_state(state='PROGRESS', meta={'progress': progress})

            _ = [x ** 2 for x in range(1000000)]
            time.sleep(0.2)

        send_progress(100, "Аудит завершён")

        return {"status": "completed", "user_id": user_id}


    finally:

        current_app.control.add_consumer("queue_1")
        cache.delete(lock_key)
        async_to_sync(channel_layer.group_send)('fruit_trading', {

            'type': 'audit_done',
            'user_id': user_id,
            'message': 'Бухгалтерський аудит завершено ✅'

        })