from channels.generic.websocket import AsyncWebsocketConsumer
import json
import base64
from uuid import uuid4
from django.core.files.base import ContentFile
from asgiref.sync import sync_to_async
from map_features.models import Message, ChatImage
from django.conf import settings

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
        user = self.scope["user"]

        if not user.is_authenticated:
            await self.close()
            return
        
        if 'message' in data and data['message']:
            message = data['message']
            await self.save_message(user, message, self.event_id)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': user.username
                }
            )
        
        if 'image' in data and data['image']:
            image_data = data['image']
            filename = data.get('filename', f"chat_image_{uuid4()}.jpg")
            
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]

            image_url = await self.save_image(user, imgstr, filename, ext)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': f"<img src='{image_url}' class='chat-img' onclick='openModal(\"{image_url}\")' />",
                    'username': user.username
                }
            )

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
    def save_image(self, user, imgstr, filename, ext):
        # Convert base64 to file and save -- Source is Stackover + Reddit
        data = ContentFile(base64.b64decode(imgstr))
        
        chat_image = ChatImage(
            user=user,
            event_id=self.event_id
        )
        
        chat_image.image.save(f"{filename}.{ext}", data, save=False)
        chat_image.save()
        
        Message.objects.create(
            user=user,
            event_id=self.event_id,
            message=f"<img src='{chat_image.image.url}' class='chat-img' />"
        )
        
        return chat_image.image.url

    @sync_to_async
    def get_chat_history(self, event_id):
        messages = Message.objects.filter(event_id=event_id).order_by('-timestamp')[:20]
        return [{"message": msg.message, "username": msg.user.username} for msg in messages]