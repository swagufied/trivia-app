# chat/consumers.py
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
import json
from functools import partial

from .socket.exceptions import ClientError
from .socket.utils import get_args_from_incoming_msg

from .socket.chat_update import chat_update_payload
from .socket.room_update import room_update_payload
from .socket.current_user_update import current_user_update_payload

from .socket.constants import TriviaConsumerConstants as constants
from .socket.auth import get_user_from_socket_ticket
from .socket.utils import socket_group_send, get_user_or_error, get_room_or_error, socket_group_add, socket_self_send
from .socket.game_update import game_update_payload 


class GameBaseConsumer(JsonWebsocketConsumer):

	commands = {
		constants.VALIDATE_CONNECTION: self.validate_connection,
		constants.JOIN_ROOM: self.join_room,
		constants.LEAVE_ROOM: self.leave_room
	}

	# allows you to add or override functions
	def add_command(self, command, function):
		commands[command] = function

	# called when the socket handshake is made
	def connect(self):
		print('connected', self.channel_name)
		
		self.accept()
		self.rooms = set() # records rooms user is in so that upon disconnect, user can be removed from them
		self.user_id = None
		self.helper = ConsumerHelper(self)

	# all messages go through here
	def receive_json(self, content):

		command = content['type']
		data = content.get('data') or dict()

		# compile arguments for processing functions
		args = []
		if command == constants.VALIDATE_CONNECTION:
			args = [data['ticket']]
		else:

			room = get_room_or_error(content['room_id'])
			user = get_user_or_error(self.user_id)
			
			# this error probably occurs because the connection hasnt been validated or because room_id was missing in the msg
			if not room or not user:
				self.helper.self_send(constants.SERVER_ERROR,{'error_msg': 'Something went wrong'})

			# build arguments
			if command == constants.JOIN_ROOM:
				args = [room, user, data['password']]
			
			# make sure the room attempting to be processed is one the user is a member of
			if not room.id in self.rooms:
				self.helper.self_send(constants.SERVER_ERROR,{'error_msg': 'Something went wrong'})

			if command == constants.LEAVE_ROOM:
				args = [room, user]
			else:
				# custom processing function
				args = [room, user, data] 

		try:
			commands[command](content['data'])
		except ClientError as e:
			self.helper.self_send(constants.SERVER_ERROR, {"error_msg": e.code})
		except Exception as e:
			print(e)

	# upon the socket disconnecting on client end
	def disconnect(self, close_code):
		user = get_user_or_error(self.user_id)

		# if no user was found, the connection probably disconnected before being verified
		if user:
			for room_id in list(getattr(self, constants.ROOMS)):
				room = get_room_or_error(room_id)

				# remove user from room if the game hasnt started yet.
				if not room.is_playing:
					try:
						self.leave_room(room, user)
					except ClientError as e:
						print('error in disconnecting', e)




	"""
	COMMAND HANDLERS
	"""
	# this should be the first connection called. validates the connection through a ticket issued at a route verified by JWT
	def validate_connection(self, ticket):

		if not ticket:
			self.helper.self_send(constants.SERVER_ERROR,{'error_msg': 'Something went wrong'})

		payload = {'is_successful': False}

		# if user ticket is validated, save the user id to the socket instance
		user = get_user_from_socket_ticket(ticket)
		if user:
			self.user_id = user.id
			payload['is_successful'] = True
		
		# notify user of successful validation
		self.helper.self_send(constants.VALIDATE_CONNECTION, payload)

	# when a user first joins a room
	def join_room(self, room, user, password):

		# the room's password must be sent with the join room request
		if room.password and room.password != password:
			self.helper.self_send(constants.JOIN_ROOM, {'is_successful': False})


		# add user to room, consumer, and socket group
		room.users.add(user)
		self.rooms.add(room.id)
		self.helper.group_add(self.channel_name, room.group_name)

		# notify user that join was successful
		self.helper.self_send(constants.JOIN_ROOM, {'is_successful': True})

		# iterate through routers available and run any that are linked to JOIN_ROOM
		for router in routers:
			if isinstance(getattr(router, constants.JOIN_ROOM), callable):
				getattr(router, constants.JOIN_ROOM)(room, user, helper)

	# when a user leaves a room. will be run upon connection disconnect
	def leave_room(self, room, user):

		room.users.remove(user)
		self.rooms.discard(room.id)

		# Remove them from the group so they no longer get room messages
		self.helper.group_remove(self.channel_name, room.group_name)
		
		# Instruct their client to finish closing the room
		self.helper.self_send(constants.LEAVE_ROOM, {'is_successful': True})


		# iterate through routers available and run any that are linked to LEAVE_ROOM
		for router in routers:
			if isinstance(getattr(router, constants.LEAVE_ROOM), callable):
				getattr(router, constants.LEAVE_ROOM)(room, user, helper)
		


	"""
	GROUP_SEND HANDLERS
	"""
	def room_join(self, event):
		# print(event)
		self.send_json(event['payload'])

	def room_leave(self, event):
		self.send_json(event['payload'])

	def message_send(self, event):
		self.send_json({
			'type': constants.UPDATE_CHAT,
			'data': event['payload']
			})

	def game_update(self, event):
		self.send_json({
			'type': constants.UPDATE_GAME,
			'data':event['payload']
			})
