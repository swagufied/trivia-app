from channels.db import database_sync_to_async
from ..models import Room
from .exceptions import ClientError
from django.contrib.auth.models import User
from .constants import TriviaConsumerConstants as constants
from asgiref.sync import async_to_sync




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


def socket_self_send(send_json, msg_type, msg_payload):
	send_json({
		'type': msg_type,
		'data': msg_payload 
		})

def socket_group_send(channel_layer,  msg_type,group_name, msg_payload):
	async_to_sync(channel_layer.group_send)(
		group_name,
		{
			'type': msg_type,
			'payload': msg_payload
		}
	)

def socket_group_add(channel_layer, channel_name, group_name):
	async_to_sync(channel_layer.group_add)(
		group_name,
		channel_name
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
	elif not data:

		if command in [constants.LEAVE_ROOM]:
			pass
		else:
			raise ClientError('MSG_DATA_MISSING')

	

	# generate args and kwargs
	if command == constants.VALIDATE_CONNECTION:

		args = [data.get('ticket')]

	else: 
		room = get_room_or_error(room_id)
		user = get_user_or_error(user_id)

		if not user:
			raise ClientError('INVALID_USER_ID')

		if not room:
			raise ClientError('INVALID_ROOM_ID')

		elif command == constants.JOIN_ROOM:
			args = [room, user, data.get('password')]
		elif command == constants.LEAVE_ROOM:
			args = [room, user]

		elif command == constants.UPDATE_CHAT:
			
			args = [room, user]
			kwargs['msg'] = data.get('message')

		elif command == constants.UPDATE_GAME:

			args = [room, user, data]
			
		else:
			raise ClientError('INVALID_COMMAND')
	
	print(command, args, kwargs)
	return command, args, kwargs

