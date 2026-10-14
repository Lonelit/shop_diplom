import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from shop.models import ChatRoom, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Подключаем покупателя к группе этой комнаты чата
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Отключаем покупателя при закрытии вкладки
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Метод срабатывает, когда КТО-ТО отправляет сообщение в JS
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_text = text_data_json['message']
        user = self.scope['user']

        if user.is_authenticated and message_text.strip():
            # Сохраняем сообщение в БД (асинхронно)
            await self.save_message(user, message_text)

            # Рассылаем сообщение ВСЕМ участникам этой комнаты
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_text,
                    'sender_username': user.username
                }
            )

    # Прием события от группы и отправка обратно в браузер (в JS)
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_username': event['sender_username']
        }))

    # Вспомогательный метод для сохранения в БД
    @database_sync_to_async
    def save_message(self, user, text):
        room = ChatRoom.objects.get(id=self.room_id)
        return Message.objects.create(room=room, sender=user, text=text)