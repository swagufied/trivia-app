from django.shortcuts import render

# Create your views here.
from django.utils.safestring import mark_safe
import json
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Room
from django.contrib.auth.models import User, Group
from rest_framework import viewsets

from rest_framework import serializers

from .socket.utils import get_room_or_error
from .models import SocketTicket
from rest_framework.decorators import api_view , permission_classes 
# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = User
#         fields = ['url' ,'username', 'email', 'rooms']

# class RoomSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Room
#         fields = ['url', 'state','data', 'users']

# class UserViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = User.objects.all().order_by('-date_joined')
#     serializer_class = UserSerializer


# class RoomViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = Room.objects.all()
#     serializer_class = RoomSerializer





class SocketTicketView(APIView):
    permission_classes = (IsAuthenticated,)

    # will return a ticket associated with the user in the token
    def get(self, request):

        socket_ticket = SocketTicket.objects.create_ticket(request.user)

        payload = {
            'ticket': str(socket_ticket.ticket)
        }        

        return Response(payload)



class RoomView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        
        room = get_room_or_error(kwargs['room_id'])

        response_content = {
            'name': room.name,
            'has_password': room.password != "",
            'is_playing': room.is_playing,
            'is_member': False
        }

        if request.user in room.users.all():
            response_content['is_member'] = True

        
        
        return Response(response_content)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_room_password(request):

    # print(request.data, dir(request))

    room = get_room_or_error(request.data.get('room_id'))

    response_content = {
        'is_successful': False
    }

    if request.data.get('password') == room.password:
        response_content['is_successful'] = True
    else:
        response_content['error'] = 'Invalid password.'

    return Response(response_content)



# GET - return list of all rooms
def rooms():
    return HttpResponse("Hello, world. You're at the trivia index.")






class TokenView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        print(request.user)
        # print(dir(request))
        content = {
            'verified': True,
            'user': {
                'username': request.user.username
                }
            }
            
        return Response(content)


