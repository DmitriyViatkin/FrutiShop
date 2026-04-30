import json
from channels.generic.websocket import AsyncWebsocketConsumer

class FruitsConsumer(AsyncWebsocketConsumer):
     GROUP = 'fruits_trading'

     async def connect(self):
         await self.channel_layer.group_add( self.GROUP, self.channel_name )
         await self.accept()
         await self.send(text_data=json.dumps({
            "message": "WebSocket підключено",
             "Balance": None
         })
         )
     async def disconnect (self, code):
         await self.channel_layer.group_discard( self.GROUP, self.channel_name )

     async def fruits_log(self, event):

         await self.send(text_data=json.dumps({
             "message": event['message'],
             "Balance": event.get['balance']
         }))