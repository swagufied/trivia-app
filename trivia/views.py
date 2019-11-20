from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view , permission_classes 
from rest_framework import viewsets

from game_server.consumer.utils import get_room_or_error
from .models import SocketTicket, Room
from django.http import HttpResponseNotFound
from game_server.tasks import invalidate_ticket


class SocketTicketView(APIView):
    permission_classes = (IsAuthenticated,)

    # will return a ticket associated with the user in the token
    def get(self, request):
        print('ticket view get', request.user)
        socket_ticket = SocketTicket.objects.create_ticket(request.user)
        print(socket_ticket)
        payload = {
            'ticket': str(socket_ticket.ticket)
        }   

        invalidate_ticket.s(socket_ticket.ticket).apply_async(countdown=30)
     

        return Response(payload)



class RoomView(APIView):
    queryset = Room.objects.all()
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
def validate_password(request, room_id=None):

    room = get_room_or_error(room_id)

    if not room:
        return HttpResponseNotFound()

    response_content = {
        'is_successful': False
    }

    if not room.password or request.data.get('password') == room.password:
        response_content['is_successful'] = True

        socket_ticket = SocketTicket.objects.create_ticket(request.user)
        
        response_content['ticket'] = str(socket_ticket.ticket)
           
        # invalidate_ticket.delay(socket_ticket.ticket)
        invalidate_ticket.apply_async(args=[str(socket_ticket.ticket)], countdown=30)

    else:
        response_content['error'] = 'Invalid password.'

    return Response(response_content)

