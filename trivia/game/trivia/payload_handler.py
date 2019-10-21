from trivia.socket.constants import TriviaConsumerConstants as constants
from .constants import TriviaConstants as game_constants
from ... import scheduler, running_games
import datetime
from .Trivia import Trivia
"""
	game_data = {
		host_id: int
		game_state: str
		
		# questions: [
			{
				question_id: int
				question: str
				answer: str (dependent on the type of question)
				player_answers: {
					user_id: int
					answer: str
				}

			}
		]
		game_settings: {}

	}

	"""




def trivia_payload_handler(socket_group_add, socket_self_send, socket_group_send, payload):

	if payload['action'] == constants.JOIN_ROOM:
		join_room_handler(socket_group_send, payload['room'], payload['user'])


	elif payload['action'] == game_constants.START_GAME:
		start_game_handler(payload['room'], socket_group_add, socket_self_send, socket_group_send)

	elif payload['action'] == game_constants.SUBMIT_ANSWER:
		submit_answer_handler(payload['room'], payload['user'], payload)

	pass



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

def start_game_handler(room, socket_group_add, socket_self_send, socket_group_send):
	running_games[room.id] = Trivia(room, socket_group_add, socket_self_send, socket_group_send)
	running_games[room.id].start_game()

def submit_answer_handler(room, user, payload):
	print(payload)
	running_games[room.id].process_answer(user.username, payload['data'])

