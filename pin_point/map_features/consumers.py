from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from django.contrib.auth.models import AnonymousUser
from map_features.models import Message, Event  # Ensure Event model is imported

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract event_id from the URL path
        self.event_id = self.scope['url_route']['kwargs']['event_id']
        self.room_group_name = f"chat_{self.event_id}"

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Load the data received from WebSocket
        data = json.loads(text_data)
        message = data['message']
        user = self.scope["user"]

        if user.is_authenticated:
            # Ensure the message is saved with the correct event_id
            await self.save_message(user, message)

            # Broadcast the message to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': user.username
                }
            )
        else:
            # Close WebSocket if the user is not authenticated
            await self.close()

    async def chat_message(self, event):
        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username']
        }))

    @sync_to_async
    def save_message(self, user, message):
        # Ensure the event_id is properly passed and the event is fetched
        event = Event.objects.get(id=self.event_id)
        
        # Create and save the message with the event_id
        Message.objects.create(user=user, event=event, message=message)

    @sync_to_async
    def get_chat_history(self, event_id):
        event = Event.objects.get(id=event_id)
        return Message.objects.filter(event=event).order_by('timestamp')  # Retrieve messages for the event
