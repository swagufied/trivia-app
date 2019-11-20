import inspect

from channels.generic.websocket import JsonWebsocketConsumer
from game_server.constants import HEARTBEAT, JOIN_ROOM, LEAVE_ROOM, AUTHENTICATE_CONNECTION, CLIENT_ERROR, ERROR
from .utils import get_user_from_socket_ticket, get_room_or_error
from .exceptions import ClientError
from channels_presence.models import Room as Group, Presence
from game_server.models import SocketTicket
from .decorators import authentication_required
from asgiref.sync import async_to_sync

from .consumer_send_functions import get_user_group_name, add_channel_to_group, remove_channel_from_group

class RoomConsumer(JsonWebsocketConsumer):


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.rooms = set()
		self.commands = self.init_commands( getattr(self, 'routers', []) )
		self.user = None
		self.is_authenticated = False
		# print('RoomConsumer.commands', self.commands)
	def init_commands(self, routers):
		
		commands = {}
		# iterate routers
		for router in routers:
			instantiated_router = router

			# if class is uninstantiated, instantiate it
			if inspect.isclass(router):
				instantiated_router = router()

			# iterate commands in router
			for command, functions in instantiated_router.get_routes().items():
				if command in commands:
					commands[command].extend(functions)
				else:
					commands[command] = functions
		return commands


	def connect(self):
		# accept connection

		self.accept()
		# Group.objects.prune_presences()


	def receive_json(self, content):

		command = content['command']
		room_id = content['room_id']
		data = content.get('data', dict())

		if command == HEARTBEAT:
			Presence.objects.touch(self.channel_name)
			return

		try:
			if command == AUTHENTICATE_CONNECTION:
				self.authenticate_connection(data['ticket'])
			elif command == JOIN_ROOM:
				self.join_room(room_id, data['password'])
			elif command == LEAVE_ROOM:
				self.leave_room(room_id)
			else:
				self.route_command(command, data, room_id=room_id)
		except ClientError as e:
			self.self_send(CLIENT_ERROR, {"error_msg": e.code})
		except Exception as e:
			print(e)
			self.self_send(ERROR, {"msg": "Something went wrong."})


	def authenticate_connection(self, ticket):
		# get socket ticket (ticket means that the user has verified the room password)
		self.user = get_user_from_socket_ticket(ticket)
		if not self.user:
			self.self_send(AUTHENTICATE_CONNECTION, {'is_successful': False})


		#invalidate ticket
		SocketTicket.objects.invalidate_ticket(ticket)

		self.is_authenticated = True

		self.self_send(AUTHENTICATE_CONNECTION, {'is_successful': True})
		print('connection authenticated', self.user.username)

	def count_user_instance_in_group(self, group_name):
		return Group.objects.filter(channel_name=group_name, presence__user=self.user).count()

	@authentication_required
	def join_room(self, room_id, password):

		# user join group and register user to room
		room = get_room_or_error(room_id)
		if room.password != password:
			self.self_send(CLIENT_ERROR, {'error_msg': 'Incorrect password.'})
			return

		# put the user in their own group - for  user_send
		user_group_name = get_user_group_name(room, self.user)
		add_channel_to_group(user_group_name, self.channel_name, self.user)

		# add user to the room group
		add_channel_to_group(room.group_name, self.channel_name, self.user)
		

		self.rooms.add(str(room_id))

		# notify room users
		self.self_send(JOIN_ROOM, {'is_successful': True})

		# if this is first instance of user in room
		# print(self.count_user_instance_in_group(room.group_name))
		# if self.count_user_instance_in_group(room.group_name)  == 1:
		self.route_command(JOIN_ROOM, {}, room=room)


	def leave_room(self, room_id):
		room = get_room_or_error(room_id)
		remove_channel_from_room(room, self.channel_name)

		# if last instance of user is gone from room
		# if self.count_user_instance_in_group(room.group_name) == 0:

			# notify room users
		self.route_command(LEAVE_ROOM, {}, room=room)


	
	def disconnect(self, close_code):
		print('disconnected')
		for room_id in self.rooms:
			try:
				self.leave_room(room_id)
			except Exception as e:
				print(e)
				continue

		
	@authentication_required
	def route_command(self, command, data, room_id=None, room=None, user=None):

		room_id = room_id or room.id
		if str(room_id) not in self.rooms:
			self.self_send(CLIENT_ERROR, {'error_msg': 'You have not joined room {} yet.'.format(room_id)})
			return

		room = room or get_room_or_error(room_id)

		for f in self.commands.get(command, list()):
			print(f, room)
			f(data, 
				room=room, 
				user=user or self.user,
				command=command
				)


	"""
	SEND FUNCTIONS
	"""
	def message_send(self, event):
		self.send_json(event['payload'])


	# to send to the user socket is connected to
	def self_send(self, msg_type: str, msg_payload: dict):
		self.send_json({
			'type': msg_type,
			'data': msg_payload 
			})

	# # to send to a group group_name
	# def group_send(self, group_name: str, msg_type: str, msg_payload: dict):
	# 	async_to_sync(self.channel_layer.group_send)(
	# 		group_name,
	# 		{
	# 			# 'type': msg_type,
	# 			'type': 'message.send',
	# 			'payload': {
	# 					'type': msg_type,
	# 					'data': msg_payload
	# 				}
	# 		}
	# 	)

	# # to add a member to a group. if the group name doesnt exist, it will automatically be created
	# def group_add(self, channel_name: str, group_name: str):
	# 	async_to_sync(self.channel_layer.group_add)(
	# 		group_name,
	# 		channel_name
	# 	)

	# def group_remove(self, channel_name: str, group_name: str):
	# 	async_to_sync(self.channel_layer.group_discard)(
	# 		group_name,
	# 		channel_name
	# 	)