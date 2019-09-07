from channels.db import database_sync_to_async
from ..models import Room
from .exceptions import ClientError
from django.contrib.auth.models import User




def get_room_or_error(room_id):
	
	if not room_id:
		return None

	try:
		room = Room.objects.get(pk=room_id)
	except Room.DoesNotExist:
		raise ClientError("INVALID_ROOM")

	return room


def get_user_or_error(user_id):
	
	if not user_id:
		return None

	try:
		user = User.objects.get(pk=user_id)
	except User.DoesNotExist:
		raise ClientError("INVALID_USER")

	return user

def socket_send(channel_layer, group_name, msg_type, msg_payload):
		async_to_sync(channel_layer.group_send)(
			group_name,
			{
				'type': msg_type,
				'payload': msg_payload
			}
		)

# return tuple - type, *args, *kwargs
def get_args_from_incoming_msg(msg, user_id=None):

	command = msg.get('type')
	args = []
	kwargs = {}

	room_id = msg.get('room_id')
	data = msg.get('data')
	

	if not command:
		raise ClientError('MSG_COMMAND_MISSING')
	elif not room_id:
		raise ClientError('MSG_ROOM_ID_MISING')
	elif not data:
		raise ClientError('MSG_DATA_MISSING')

	room = get_room_or_error(room_id)

	# generate args and kwargs
	if command == constants.VALIDATE_CONNECTION:

		args = [room, data.get('ticket')]

	user = get_user_or_error(user_id)
	if not user:
		raise ClientError('INVALID_USER_ID')

	if command in [constants.JOIN_ROOM, constants.LEAVE_ROOM]:

		args = [room, user]

	if command == constants.UPDATE_CHAT:
		
		args = [room, user]
		kwargs['msg'] = data.get('message')

	elif command == constants.UPDATE_GAME:

		args = [room, user, data]
		
	else:
		raise ClientError('INVALID_COMMAND')
	

	return command, args, kwargs

