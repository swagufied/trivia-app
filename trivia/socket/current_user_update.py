from .constants import TriviaConsumerConstants as constants


def current_user_update_payload(command, *args, **kwargs):

	commands = {
		# constants.VALIDATE_CONNECTION: validate_connection,
		constants.JOIN_ROOM: join_room,
		constants.LEAVE_ROOM: leave_room,
		# constants.UPDATE_CHAT: self.update_chat,
		# constants.UPDATE_GAME: self.update_game
	}

	return {
		'type': command,
		'data': commands[command](*args, **kwargs)
		}


def validate_connection():
	pass

def join_room(is_successful):

	data = {
		'is_successful': is_successful,
	}


	# print('join_room payload', data)
	return data

def leave_room(is_successful):

	data = {
		'is_successful': is_successful
	}
	return data