import json

from channels.db import database_sync_to_async
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from psycopg import transaction


class FruitsConsumer(AsyncWebsocketConsumer):
    GROUP = 'fruit_trading'

    async def connect(self):
        await self.channel_layer.group_add(self.GROUP, self.channel_name)
        await self.accept()
        history = await self.get_recent_transactions()
        for msg in history:
            await self.send(text_data=json.dumps(msg))
        await self.send(text_data=json.dumps({
            "message": "WebSocket підключено",
            "balance": None
        }))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.GROUP, self.channel_name)

    @database_sync_to_async
    def get_recent_transactions(self):
        from trading.models import OrderTransaction, Account
        transactions = OrderTransaction.objects.order_by('-created_at')[:50]
        try:
            account = Account.objects.first()
            balance = str(account.balance) if account else None
        except Exception:
            balance = None

        result = []
        for tx in transactions:
            if tx.success:
                msg = (f"✅ {tx.created_at.strftime('%d.%m.%Y %H:%M')} — "
                       f"{tx.get_transaction_type_display().upper()} {tx.fruit.upper()} "
                       f"x{tx.quantity} @ ${tx.price}")
            else:
                reason = tx.get_reason_display() if tx.reason else 'Помилка'
                msg = (f"❌ {tx.created_at.strftime('%d.%m.%Y %H:%M')} — "
                       f"{tx.get_transaction_type_display().upper()} {tx.fruit.upper()} "
                       f"x{tx.quantity} — {reason}")
            result.append({"message": msg, "balance": None})

        if result and balance:
            result[-1]["balance"] = balance
        return result

    async def fruit_log(self, event):
        await self.send(text_data=json.dumps({
            "message": event['message'],
            "balance": event.get('balance'),
            "error": event.get('error', False)
        }))
    async def audit_progress (self, event):
        await self.send(text_data=json.dumps({
            "message": event.get('message',""),
            "progress" : event['progress'],

        }))

class ChatConsumer(AsyncWebsocketConsumer):
     GROUP = 'chat'

     async def connect(self):
         await self.channel_layer.group_add( self.GROUP, self.channel_name )
         await self.accept()

     async def disconnect (self, code):
         await self.channel_layer.group_discard( self.GROUP, self.channel_name )

     async def receive(self, text_data):

         data = json.loads(text_data)
         username = self.scope['user'].username or "Анонім"
         await  self.channel_layer.group_send(self.GROUP, {
             'type': 'chat_message',
             'message': data.get('message', ''),
             'username': username,
             'time': timezone.now().strftime('%H:%M')

         })
     async def chat_message(self, event):
         await self.send(text_data = json.dumps({
            'message': event['message'],
             'username': event['username'],
             'time': event['time']
         })
         )
