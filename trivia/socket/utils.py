from channels.db import database_sync_to_async
from ..models import Room
from .exceptions import ClientError
from django.contrib.auth.models import User
from .constants import TriviaConsumerConstants as constants
from asgiref.sync import async_to_sync


from ..models import SocketTicket


def get_room_or_error(room_id):
	
	if not room_id:
		return None

	try:
		room_id = int(room_id)
		# print('getting room')
		room = Room.objects.get(pk=room_id)
		# print('retreived room', room)
	except Room.DoesNotExist:
		raise ClientError("INVALID_ROOM")
	except Exception as e:
		print(e)
	return room


def get_user_or_error(user_id):
	
	if not user_id:
		return None

	try:
		user = User.objects.get(pk=user_id)
		# print('user', user)
	except User.DoesNotExist:
		raise ClientError("INVALID_USER")

	return user

def get_user_from_socket_ticket(ticket):

	ticket_row = SocketTicket.objects.filter(pk=ticket).first()

	# make sure ticket time is still valid
	if ticket_row: # and utcnow - ticket_row.date <= 5min:
		return ticket_row.user

	return None
