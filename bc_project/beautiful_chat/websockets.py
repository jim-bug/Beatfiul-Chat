from channels.generic.websocket import AsyncWebsocketConsumer
from beautiful_chat.models import Chat
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from channels.auth import get_user
import json, asyncio

# Map of active chat rooms to their respective consumers
chat_rooms = {}

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = await get_user(self.scope)

        # Check if the user is authenticated
        if self.user.is_authenticated:
            await self.accept()
            # Get the chat_id from the URL
            self.chat_id = self.scope['url_route']['kwargs']['chat_id']

            if self.chat_id not in chat_rooms:
                # Check if the chat exists
                chat = await self.get_chat()
                if chat is None:
                    await self.send(text_data=json.dumps({
                        'error': 'Chat does not exist'
                    }))
                    return
                # Add the consumer to the chat room
                chat_rooms[self.chat_id] = [self]
            else:
                # Add the consumer to the chat room
                chat_rooms[self.chat_id].append(self)
        else:
            # Close the connection if the user is not authenticated
            await self.close()
        
    @database_sync_to_async
    def get_chat(self):
        return Chat.objects.filter(chat_id=self.chat_id).first()

    async def disconnect(self, close_code):
        # Remove the consumer from the chat room
        if self.chat_id in chat_rooms and self in chat_rooms[self.chat_id]:
            chat_rooms[self.chat_id].remove(self)
        pass

    async def receive(self, text_data):
        pass

    # Send the message to the consumer
    async def send_message(self, event):
        await self.send(text_data=json.dumps(event))

@async_to_sync
async def send_message_to_chat(chat_id, event):
    if chat_id in chat_rooms:
        # Create a list to hold the tasks
        tasks = []

        for consumer in chat_rooms[chat_id]:
            # Create a new task for each consumer
            task = consumer.send_message(event)
            tasks.append(task)

        # Run the tasks concurrently
        await asyncio.gather(*tasks)