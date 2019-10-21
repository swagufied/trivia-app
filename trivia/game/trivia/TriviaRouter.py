from trivia.socket.BaseRouter import BaseRouter
from .constants import TRIVIA
from trivia.socket.decorators import game_type





class TriviaRouter(BaseRouter):

	@game_type(TRIVIA)
	def join_room(self, room, user, helper):

		payload = {
			'type': UPDATE_PLAYERS,
			'data':{
				'players': get_players_info(room, user),
				}
		}

		helper.group_send(room.group_name, 'game.update', payload)

	# def leave_room():
	# 	pass

	# def update

def get_players_info(room, user):

	players = []
	for player in room.users.all():

		score = 0
		if 'scores' in room.game_data:
			score = room.game_data['scores'][player.id]

		players.append({
				'username': player.username,
				'score': score,
				'is_host': room.host.id == player.id,
				'is_self': player.id == user.id
			})
	return players