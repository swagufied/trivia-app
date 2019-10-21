from channels.generic.websocket import JsonWebsocketConsumer
from .exceptions import ClientError
from .consumer_constants import VALIDATE_CONNECTION, JOIN_ROOM, LEAVE_ROOM, UPDATE_ROOM, SERVER_ERROR, CLIENT_ERROR
from .utils import get_room_or_error, get_user_or_error, get_user_from_socket_ticket
from .. import routers
import inspect
from .ConsumerHelper import ConsumerHelper

class BaseRoomConsumer(JsonWebsocketConsumer):

	def __init__(self, *args, **kwargs):

		# this will redirect socket messages to appropriate functions
		self.commands = {
			VALIDATE_CONNECTION: self.validate_connection,
			JOIN_ROOM: self.join_room,
			LEAVE_ROOM: self.leave_room
		}

		# go through each router and map their unique commands
		self.routers = {}
		for router in routers:

			# if class is uninstantiated, instantiate it
			if inspect.isclass(router):
				router = router()

			for command, function in router.get_routes().items():
				if command in self.routers:
					self.routers[command].append(function)
				else:
					self.routers[command] = [function]

		super().__init__(*args, **kwargs)

	# allows you to add or override functions
	def add_command(self, command, function):
		self.commands[command] = function

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
		if command == VALIDATE_CONNECTION:
			args = [data['ticket']]
		else:

			room = get_room_or_error(content['room_id'])
			user = get_user_or_error(self.user_id)
			
			# this error probably occurs because the connection hasnt been validated or because room_id was missing in the msg
			if not room or not user:
				self.helper.self_send(CLIENT_ERROR,{'error_msg': 'Something went wrong'})

			# build arguments
			if command == JOIN_ROOM:
				args = [room, user, data.get('password')]
			else:
				# make sure the room attempting to be processed is one the user is a member of
				if not room.id in self.rooms:
					self.helper.self_send(CLIENT_ERROR, {'error_msg': 'Something went wrong'})
					raise ClientError("Either wrong room_id was provided or server failed to add room to consumer.rooms")

				if command == LEAVE_ROOM:
					args = [room, user]
				else:
					# custom processing function
					args = [room, user, self.helper, data] 

		try:
			self.commands[command](*args)
		except ClientError as e:
			self.helper.self_send(CLIENT_ERROR, {"error_msg": e.code})
		except Exception as e:
			print(e)

	# upon the socket disconnecting on client end
	def disconnect(self, close_code):
		user = get_user_or_error(self.user_id)

		# if no user was found, the connection probably disconnected before being verified
		if user:
			for room_id in list(self.rooms):
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
			self.helper.self_send(CLIENT_ERROR,{'error_msg': 'Something went wrong'})

		payload = {'is_successful': False}

		# if user ticket is validated, save the user id to the socket instance
		user = get_user_from_socket_ticket(ticket)
		if user:
			self.user_id = user.id
			payload['is_successful'] = True
		
		# notify user of successful validation
		self.helper.self_send(VALIDATE_CONNECTION, payload)

	# when a user first joins a room
	def join_room(self, room, user, password):

		# the room's password must be sent with the join room request
		if room.password and room.password != password:
			self.helper.self_send(JOIN_ROOM, {'is_successful': False})


		# add user to room, consumer, and socket group
		room.users.add(user)
		self.rooms.add(room.id)
		self.helper.group_add(self.channel_name, room.group_name)

		# notify user that join was successful
		self.helper.self_send(JOIN_ROOM, {'is_successful': True})

		# iterate through routers available and run any that are linked to JOIN_ROOM
		for function in self.routers[JOIN_ROOM]:
			function(room, user, self.helper)

	# when a user leaves a room. will be run upon connection disconnect
	def leave_room(self, room, user):

		room.users.remove(user)
		self.rooms.discard(room.id)

		# Remove them from the group so they no longer get room messages
		self.helper.group_remove(self.channel_name, room.group_name)
		
		# Instruct their client to finish closing the room
		self.helper.self_send(LEAVE_ROOM, {'is_successful': True})


		# iterate through routers available and run any that are linked to LEAVE_ROOM
		for function in self.routers[LEAVE_ROOM]:
			function(room, user, self.helper)
		


	"""
	GROUP_SEND HANDLERS
	"""
	# these functions are called when a group_send message is emitted. formality of django channels
	def room_join(self, event):
		self.helper.self_send(JOIN_ROOM, event['payload'])

	def room_leave(self, event):
		self.helper.self_send(LEAVE_ROOM, event['payload'])

	def room_update(self, event):
		self.helper.self_send(UPDATE_ROOM, event['payload'])
	