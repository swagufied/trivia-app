import datetime
from .constants import TriviaConsumerConstants as constants


def chat_update_payload(command, *args, **kwargs):
	commands = {
		# constants.VALIDATE_CONNECTION: validate_connection,
		constants.JOIN_ROOM: join_room,
		constants.LEAVE_ROOM: leave_room,
		constants.UPDATE_CHAT: update_chat,
		# constants.UPDATE_GAME: self.update_game
	}
	return {
		'type': constants.UPDATE_CHAT,
		'data': commands[command](*args, **kwargs)
		}

def join_room(user):
	data = {
		'username': None,
		'message': "{} has joined".format(user.username),
		'date': datetime.datetime.now().isoformat()
	}
	return data

def leave_room(user):
	data = {
		'username': None,
		'message': "{} has left".format(user.username),
		'date': datetime.datetime.now().isoformat()
	}
	return data



def update_chat(user, message):
	data = {
		'username': user.username,
		'message': message,
		'date': datetime.datetime.now().isoformat()
	}
	return data
	

		




	