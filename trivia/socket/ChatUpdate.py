import datetime

class ChatUpdate:



	def msg(user, message: str):
	
		data = {
			'username': user.username,
			'message': message,
			'date': datetime.datetime.now().isoformat()
		}
		return data
	
	def join_room(user, empty_msg):

		data = {
			'username': None,
			'message': "{} has joined".format(user.username),
			'date': datetime.datetime.now().isoformat()
		}
		return data

	def leave_room(user, empty_msg):
		data = {
			'username': None,
			'message': "{} has left".format(user.username),
			'date': datetime.datetime.now().isoformat()
		}
		return data


	