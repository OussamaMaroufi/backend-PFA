import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from message.models import Thread, UserMessage
from users.models import UserProfile
from django.contrib.auth.models import User
from django.db.models import Q


class ChatConsumer(AsyncWebsocketConsumer):

    def getUser(self, userId):

        return UserProfile.objects.get(user=userId)

    def saveMessage(self, message, userId, threadId):
        userObj = UserProfile.objects.get(user=userId)
        threadObj = Thread.objects.get(id=threadId)
        chatMessageObj = UserMessage.objects.create(
            thread=threadObj, sender=userObj, body=message
        )
        return {
            'action': 'message',
            'user': userId,
            'threadId': threadId,
            'message': chatMessageObj.body,
            'messageId':str(chatMessageObj.id),
            'username': userObj.username,
            'timestamp': str(chatMessageObj.timestamp),
            'imgUrl':str(userObj.profile_pic)
            #Add img url 
        }

    async def connect(self):
        self.userId = self.scope['url_route']['kwargs']['userId']
        self.user = await database_sync_to_async(self.getUser)(self.userId)
        self.userThreads = await database_sync_to_async(
            list
        )(Thread.objects.filter(Q(sender=self.user) | Q(reciever=self.user)))

        for thread in self.userThreads:
            print("this thread id", thread.id)
            await self.channel_layer.group_add(
                str(thread.id),
                self.channel_name
            )
        await self.accept()

    async def disconnect(self, close_code):
        for thread in self.userThreads:
            await self.channel_layer.group_discard(
                str(thread.id),
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        threadId = text_data_json['threadId']
        chatMessage = {}

        if action == 'message':
            message = text_data_json['message']
            print("your message", message)
            userId = text_data_json['user']
            chatMessage = await database_sync_to_async(
                self.saveMessage
            )(message, userId, threadId)
        elif action == 'typing':
            chatMessage = text_data_json

        await self.channel_layer.group_send(
            threadId,
            {
                'type': 'chat_message',
                'message': chatMessage
            }
        )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))
