from .ChatUpdate import ChatUpdate
from .RoomUpdate import RoomUpdate
from .constants import TriviaConsumerConstants as constants
from ..game.standard import StandardTrivia
# from ...anime_database.celery import app

'''
CONSTANTS
'''
from ..tasks import *




'''
GENERIC FUNCTIONS
'''
def construct_payload(payload_type, data):

	return {
		'type': payload_type,
		'data': data
	}



# user must be user query
def chat_update(msg_type, user, message):
	
	if msg_type not in ['msg', 'join_room', 'leave_room']:
		raise Exception('Invalid msg_type')

	data = getattr(ChatUpdate, msg_type)(user, message)
	
	return construct_payload(constants.UPDATE_CHAT, data)


"""
# must take in a dict
{
	update_type: necessary data
}

returns
{
	type: UPDATE_ROOM,
	data: {
		update_type: processed data
	}
}
"""

def room_update(room, updates: dict):

	data = {}

	for key in updates:

		if key not in ['player_list', 'is_host']:
			raise Exception('Invalid room update')

		data[key] = getattr(RoomUpdate, key)(updates[key])

	return construct_payload(constants.UPDATE_ROOM, data)


"""

return - dict - the info that will for in the "data" key of outgoing message
"""

def generate_payload(type, *args, result=False, **kwargs):

	commands = {
		constants.VALIDATE_CONNECTION: self.validate_connection,
		constants.JOIN_ROOM: join_room,
		constants.LEAVE_ROOM: self.leave_room,
		constants.UPDATE_CHAT: self.update_chat,
		constants.UPDATE_GAME: self.update_game
	}


	return 

	def generate(type, *args, **kwargs):

		return payload

'''
COMPOSITE PAYLOADS
'''
def join_room_status(user, success: bool):


	
	data = {
		'is_successful': success,
		'user': {
			'username': user.username
		}
	}
	# print('join_room payload', data)
	return construct_payload('JOIN_ROOM', data)


def join_room(room, user):

	payload = []

	payload.append(
		room_update(room, 
			{
				'player_list': room.users.all(),
				# 'is_host': room.data.get('host_id') == user.id
			}
		)
	)

	payload.append(
		chat_update('join_room', user, None)
	)

	return payload



def leave_room(room, user):
	payload = []

	payload.append(
		room_update(room, {
				'player_list': room.users.all()
			}
		)
	)

	payload.append(
		chat_update('leave_room', user, None)
	)

	return payload

