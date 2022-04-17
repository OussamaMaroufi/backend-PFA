from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from users.models import UserProfile
from .serializers import MessageSerializer, ThreadSerializer,ThreadSerializerForCreate
from .models import UserMessage, Thread
from django.db.models import Q


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def read_message(request, pk):
    try:
        thread = Thread.objects.get(id=pk)
        messages = thread.messages.all()
        un_read = thread.messages.filter(is_read=False)
        for msg in un_read:
            msg.is_read = True
            msg.save()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'details': f"{e}"}, status=status.HTTP_204_NO_CONTENT)

# This  View to Count unread Messages


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_un_read_count(request):
    user = request.user.userprofile
    threads = Thread.objects.filter(Q(sender=user) | Q(reciever=user))
    count = 0

    for thread in threads:
        messages = thread.messages.all()
        un_read = thread.messages.filter(is_read=False)

        count = count + un_read.count()
        print(count)

    return Response({'count': count})


# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# def CreateThread(request):
    # data = request.user

    # sender = UserProfile.objects.get(user=data)

    # print("sender",sender)
    # print("sende",sender)
    # recipient = UserProfile.objects.get(user=3)


    # recipient = UserProfile.objects.get(id=recipient_id)
    # print("recipient", recipient)
    # if recipient is not None:
    #     try:
    #         thread = Thread.objects.filter(
    #             Q(sender=sender, reciever=recipient) | Q(sender=recipient, reciever=sender))

    #         print("THread  kkk",thread)
    #         if(not thread.count()):
    #             print("THread Not exist we will create it  ")
    #             thread = Thread.objects.create(
    #                 sender=sender, reciever=recipient)
    #             print("THis is a THread data",thread)
    #             serializer = ThreadSerializer(thread, many=False)
    #             return Response(serializer.data)
            
    #         #if serializer exist 
    #         serializer = ThreadSerializer(thread,many=False)
    #         return Response(serializer.data)
          

    #     except UserProfile.DoesNotExist:
    #         return Response({'detail': 'User with that id doesnt not exists'})
    # else:
    #     return Response({'details': 'Recipient id not found'})

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def CreateThread(request):

    sender = request.user.userprofile
    recipient_id = request.data.get('recipient_id')
    print("recipient",recipient_id)
    recipient = UserProfile.objects.get(id=str(recipient_id))
    print(recipient)
    if recipient_id is not None:
        try:
            thread,created = Thread.objects.get_or_create(sender=sender,reciever=recipient)
            serializer = ThreadSerializer(thread, many=False)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({'detail':'User with that id doesnt not exists'})
    else:
        return Response({'details':'Recipient id not found'})



@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_threads(request):
    user = request.user.userprofile
    threads = Thread.objects.filter(Q(sender=user) | Q(reciever=user))
    serializer = ThreadSerializer(threads, many=True)
    print("threads",threads)
    return Response(serializer.data)

# This View to Return messages for a specific thread


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_messages(request, pk):
    user = request.user.userprofile
    messages = UserMessage.objects.filter(thread__id=pk)
    serializer = MessageSerializer(messages, many=True)
    # print("messages", serializer.data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def create_message(request):

    sender = request.user.userprofile
    data = request.data
    thread_id = data.get('thread_id')
    if thread_id:
        message = data.get('message')
        thread = Thread.objects.get(id=thread_id)
        if thread:
            if message is not None:
                message = UserMessage.objects.create(
                    thread=thread, sender=sender, body=message)
                message.save()
                serializer = ThreadSerializer(thread, many=False)
                return Response(serializer.data)
            else:
                return Response({'details': 'Content for message required'})
        else:
            return Response({'details': 'Thread not found'})
    else:
        return Response({'details': 'Please provide other user id'})
