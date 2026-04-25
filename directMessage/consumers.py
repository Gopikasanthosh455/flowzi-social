import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser, User

from directMessage.models import Message


def room_name_for(user_a, user_b):
    usernames = sorted([user_a, user_b])
    return f"chat_{usernames[0]}_{usernames[1]}"


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user or isinstance(user, AnonymousUser):
            await self.close()
            return

        self.current_user = user
        self.target_username = self.scope["url_route"]["kwargs"]["username"]
        self.room_group_name = room_name_for(self.current_user.username, self.target_username)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        payload = json.loads(text_data or "{}")
        body = (payload.get("body") or "").strip()

        if not body:
            return

        message_data = await self._persist_message(body)
        if not message_data:
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": message_data,
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    @sync_to_async
    def _persist_message(self, body):
        try:
            target_user = User.objects.get(username=self.target_username)
        except User.DoesNotExist:
            return None

        if target_user == self.current_user:
            return None

        return Message.send_message(self.current_user, target_user, body).serialize()
