# chat/consumers.py
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
import json


from .socket.exceptions import ClientError
from .socket.utils import get_args_from_incoming_msg

from .socket.chat_update import chat_update_payload
from .socket.room_update import room_update_payload
from .socket.current_user_update import current_user_update_payload

from .socket.constants import TriviaConsumerConstants as constants
from .socket.auth import get_user_from_socket_ticket
from .socket.utils import socket_send, get_user_or_error, get_room_or_error

"""
	all incoming messages must be in the following format
	{
		type: str
		room_id: int
		data: dict
	}

	all return messages will be in following format:
	{
		type: str 
		data: return
	}

	VALIDATE_CONNECTION
	data = {
		ticket: str
	}

	return = {
		is_successful: bool
	}

	JOIN_ROOM
	data = {}
	return = {TODO}

	LEAVE_ROOM
	data = {}
	return = {TODO}

	UPDATE_CHAT
	data = {
		'message': str
	}

	UPDATE_GAME
	data = {
		TODO
	}
	"""
class TriviaConsumer(JsonWebsocketConsumer):

	def connect(self):
		self.accept()

		setattr(self, constants.ROOMS, set())
		setattr(self, constants.DATA, dict())


	def receive_json(self, content):

		commands = {
			constants.VALIDATE_CONNECTION: self.validate_connection,
			constants.JOIN_ROOM: self.join_room,
			constants.LEAVE_ROOM: self.leave_room,
			constants.UPDATE_CHAT: self.update_chat,
			constants.UPDATE_GAME: self.update_game
		}

		print('incoming_json', content)
		

		try:
			command, args, kwargs = get_args_from_incoming_msg(content, user_id = getattr(self, constants.DATA).get(constants.USER_ID))
			commands[command](*args, **kwargs)
		except ClientError as e:
			self.send_json({"error": e.code})

	def disconnect(self, close_code):
		user = get_user_or_error(getattr(self, constants.DATA).get(constants.USER_ID))

		if user:

			for room_id in list(getattr(self, constants.ROOMS)):
				room = get_room_or_error(room_id)
				try:
					self.leave_room(room, user)
				except ClientError as e:
					print('error in disconnecting', e)



	"""
	COMMAND HANDLERS
	"""

	def validate_connection(self, room, ticket):

		if not ticket:
			raise ClientError('TICKET_MISSING')

		payload = {'is_successful': False}

		user = get_user_from_socket_ticket(ticket)

		if user:
			getattr(self, constants.DATA)[constants.USER_ID] = user.id
			payload['is_successful'] = True
			
		self.send_json({
			'type':constants.VALIDATE_CONNECTION, 
			'data':payload
			})


	def join_room(self, room, user, password):

		if not user:
			return

		if room.password:
			if room.password != password:
				raise ClientError('INCORRECT_PASSWORD')


		# add user to room
		room.users.add(user)
		# add room to consumer instance
		getattr(self, constants.ROOMS).add(room.id)

		# notify user that join was successful
		self.send_json(current_user_update_payload(constants.JOIN_ROOM, True))

		# make sure user can get messages from other room members
		async_to_sync(self.channel_layer.group_add)(
			room.group_name,
			self.channel_name
		)

		# notify everyone that new member joined - send out new member list
		socket_send(self.channel_layer, room.group_name, 'room.join', chat_update_payload(constants.JOIN_ROOM, user))
		socket_send(self.channel_layer, room.group_name, 'room.join', room_update_payload(constants.JOIN_ROOM, room))



	def leave_room(self, room, user):

		if not user:
			return

		room.users.remove(user)
		# Remove that we're in the room
		self.rooms.discard(room.id)

		# Remove them from the group so they no longer get room messages
		async_to_sync(self.channel_layer.group_discard)(
			room.group_name,
			self.channel_name,
		)
		socket_send(self.channel_layer, room.group_name, 'room.leave', chat_update_payload(constants.LEAVE_ROOM, user))
		socket_send(self.channel_layer, room.group_name, 'room.leave', room_update_payload(constants.LEAVE_ROOM, room))
		
		
		# Instruct their client to finish closing the room
		self.send_json(current_user_update_payload(constants.LEAVE_ROOM, True))


	def update_chat(self, room, user, msg=""):

		if not msg or not user:
			return

		if user not in getattr(self, constants.ROOMS):
			raise ClientError('NOT_A_ROOM_MEMBER')

		socket_send(self.channel_layer, room.group_name, 'message.send', chat_update_payload(constants.UPDATE_CHAT, user, msg))


	def update_game(self, room, user, data):

		# make sure the room id provided is one the user is in
		if not room.id in self.rooms:
			self.send_json({
				"LEAVE_ROOM": str(room.id),
			})


		for payload in game_update(self, user, room, data):
			async_to_sync(self.channel_layer.group_send)(
				room.group_name,
				{
					'type': 'game.update',
					'payload': payload
				}
			)


	"""

		# args - (channel_layer, group_name, msg_type, msg_payload)
		@shared_task
		def celery_send(*args):
			send(*args)

		def send(channel_layer, group_name, msg_type, msg_payload):
			async_to_sync(channel_layer.group_send)(
				group_name,
				{
					'type': msg_type,
					'payload': msg_payload
				}
			)

	"""

	"""
	GROUP_SEND HANDLERS
	"""
	def room_join(self, event):
		print(event)
		self.send_json(event['payload'])

	def room_leave(self, event):
		self.send_json(event['payload'])

	def message_send(self, event):
		print('message sent', event)
		self.send_json(event['payload'])

	def game_update(self, event):
		self.send_json(event['payload'])
