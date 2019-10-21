from trivia.socket.BaseRouter import BaseRouter
from .constants import UPDATE_CHAT
import datetime

class ChatRouter(BaseRouter):

	def join_room(self, room, user, helper):

		payload = {
			'username': None,
			'message': "{} has joined".format(user.username),
			'date': datetime.datetime.now().isoformat()
		}
		
		helper.group_send(room.group_name, 'message.send', payload)

	def leave_room(self, room, user, helper):

		payload = {
			'username': None,
			'message': "{} has left".format(user.username),
			'date': datetime.datetime.now().isoformat()
		}
		

		helper.group_send(room.group_name, 'message.send', payload)

	def update_chat(self, room, user, helper, data):

		# don't bother processing messages that are empty
		if not data['message']:
			return

		payload = {
			'username': user.username,
			'message': data['message'],
			'date': datetime.datetime.now().isoformat()
		}
		

		helper.group_send(room.group_name, 'message.send', payload)


	def get_routes(self):

		routes = {
			UPDATE_CHAT: self.update_chat
		}

		return super().get_routes(routes=routes)