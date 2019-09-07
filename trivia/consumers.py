# chat/consumers.py
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
import json


from .socket.payload import join_room, join_room_result, leave_room, chat_update, game_update
from .socket.exceptions import ClientError
from .socket.utils import get_args_from_incoming_msg


from .socket.constants import TriviaConsumerConstants as constants

"""
	all incoming messages must be in the following format
	{
		type: str
		room_id: int
		data: dict
	}

	all return messages will be in following format:
	{
		type: str (will be the same as the incoming message),
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
		command, args, kwargs = get_args_from_incoming_msg(content, user_id = getattr(self, constants.DATA).get(constants.USER_ID))

		try:
			commands[command](*args, **kwargs)
		except ClientError as e:
			self.send_json({"error": e.code})

	def disconnect(self, close_code):
		for room_id in list(self.rooms):
			try:
				self.leave_room(room_id)
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
			self.data_[constants.USER_ID] = user.id
			payload['is_successful'] = True
			
		socket_send(self.channel_layer, room.group_name, constants.VALIDATE_CONNECTION, payload)


	

	def join_room(self, room, user):


		# add user to room
		room.users.add(user)


		# add room
		self.rooms.add(room.id)

		# notify user that join was successful\
		self.send_json(join_room_result(user, True))

		# make sure user can get messages from other room members
		async_to_sync(self.channel_layer.group_add)(
			room.group_name,
			self.channel_name
		)

		# notify everyone that new member joined - send out new member list

		for payload in join_room(room, user):
			print('sending payload', payload)
			async_to_sync(self.channel_layer.group_send)(
				room.group_name,
				{
					'type': 'room.join',
					'payload': payload
				}
			)



	def leave_room(self, room, user):

		room.users.remove(user)

		for payload in leave_room(room, user):
			async_to_sync(self.channel_layer.group_send)(
				room.group_name,
				{
					'type': 'room.leave',
					'payload': payload
				}
			)
		# Remove that we're in the room
		self.rooms.discard(room_id)
		# Remove them from the group so they no longer get room messages
		self.channel_layer.group_discard(
			room.group_name,
			self.channel_name,
		)
		# Instruct their client to finish closing the room
		self.send_json({
			"LEAVE_ROOM": str(room.id),
		})


	def update_chat(self, room, user, msg=""):

		if not msg:
			return

		async_to_sync(self.channel_layer.group_send)(
			room.group_name,
			{
				'type': 'msg.send',
				'payload': chat_update('msg', user, data['message'])
			}
		)
		print('update_chat finished')

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

	def msg_send(self, event):
		print('message sent', event)
		self.send_json(event['payload'])

	def game_update(self, event):
		self.send_json(event['payload'])
