from ..models import Room, SocketTicket
from .exceptions import ClientError
from django.contrib.auth.models import User


def get_room_or_error(room_id):
	
	if not room_id:
		return None

	try:
		room = Room.objects.get(pk = int(room_id))
	except Room.DoesNotExist:
		raise ClientError("INVALID_ROOM")
	except Exception as e:
		raise e
	return room


def get_user_or_error(user_id):
	
	if not user_id:
		return None

	try:
		user = User.objects.get(pk=int(user_id))
	except User.DoesNotExist:
		raise ClientError("INVALID_USER")
	except Exception as e:
		raise e
	return user

def get_user_from_socket_ticket(ticket):

	if not ticket:
		return None

	ticket_row = SocketTicket.objects.filter(pk=ticket).first()

	# make sure ticket time is still valid
	if ticket_row: # and utcnow - ticket_row.date <= 5min:
		return ticket_row.user

	return None
