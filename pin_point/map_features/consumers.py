from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from map_features.models import Message  

# Initial Concept from django.channels Documentation - https://channels.readthedocs.io/en/latest/topics/consumers.html#basic-layout
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.event_id = self.scope['url_route']['kwargs']['event_id']
        self.room_group_name = f"chat_{self.event_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        messages = await self.get_chat_history(self.event_id)
        await self.send(text_data=json.dumps({
            "type": "chat_history",
            "messages": messages
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        user = self.scope["user"]

        if user.is_authenticated:
            await self.save_message(user, message, self.event_id)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': user.username
                }
            )
        else:
            await self.close()

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username']
        }))

    @sync_to_async
    def save_message(self, user, message, event_id):
        Message.objects.create(user=user, message=message, event_id=event_id)

    @sync_to_async
    def get_chat_history(self, event_id):
        messages = Message.objects.filter(event_id=event_id).order_by('-timestamp')[:20]
        return [{"message": msg.message, "username": msg.user.username} for msg in messages]
