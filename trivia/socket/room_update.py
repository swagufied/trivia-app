from .constants import TriviaConsumerConstants as constants


def room_update_payload(command, room, *args, **kwargs):

	commands = {
		# constants.VALIDATE_CONNECTION: validate_connection,
		constants.JOIN_ROOM: join_room,
		constants.LEAVE_ROOM: leave_room,
		# constants.UPDATE_CHAT: self.update_chat,
		# constants.UPDATE_GAME: self.update_game
	}

	room = Room(room)

	return {
		'type': command,
		'data': commands[command](room, *args, **kwargs)
		}

def join_room(room):
	data = {
		'players': room.players
	}
	return data

def leave_room(room):
	data =  {
		'players': room.players
	}
	return data


"""
Room Properties
"""
class Room:

	def __init__(self, room):
		self.room = room

	@property
	def id(self):
		return self.room.id

	@property
	def players(self):
		players = []
		users = self.room.users.all()
		for user in users:
			players.append({
					'username': user.username
				})
		return players

	def host(self):
		return self.room.host

