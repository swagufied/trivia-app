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
            'ticket': socket_ticket.ticket
        }        

        return Response(payload)



class RoomView(APIView):

    def get(self, request):


        # if no room id was given


        # if a room id was given
        pass

# GET - return list of all rooms
def rooms():
    return HttpResponse("Hello, world. You're at the trivia index.")

# GET - return details of a room
# auth required
def room(request, room_id):
	print(room_id)

	room_row = Room.objects.get(pk=room_id)

	return HttpResponse("Hello, world. You're at the room index.")






class TokenView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        print(request.user)
        print(dir(request))
        content = {
            'verified': True,
            'username': request.user.username
            }
        return Response(content)


