class ChatRouter(ApplicationRouter):

	def __init__(self):

		# map commands to functions
		setattr(self, constants.JOIN_ROOM, self.join_room)
		setattr(self, constants.LEAVE_ROOM, self.leave_room)
		setattr(self, constants.UPDATE_CHAT, self.update_chat)

		super().__init__()

	def join_room(self, room, user):

		payload = {
			'username': None,
			'message': "{} has joined".format(user.username),
			'date': datetime.datetime.now().isoformat()
		}
		

		group_send(room.group_name, 'message.send', payload)

	def leave_room(self, room, user):

		payload = {
			'username': None,
			'message': "{} has left".format(user.username),
			'date': datetime.datetime.now().isoformat()
		}
		

		group_send(room.group_name, 'message.send', payload)

	def update_chat(self, room, user, message):

		# don't bother processing messages that are empty
		if not message:
			return

		payload = {
			'username': user.username,
			'message': message,
			'date': datetime.datetime.now().isoformat()
		}
		

		group_send('message.send',  room.group_name, payload)

