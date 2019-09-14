from trivia.socket.constants import TriviaConsumerConstants as constants
from .constants import TriviaConstants as game_constants
from ... import scheduler
import datetime

"""
	game_data = {
		host_id: int
		game_state: str
		
		questions: [
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

def trivia_payload_handler(group_add, socket_self_send, socket_group_send, payload):

	if payload['action'] == constants.JOIN_ROOM:
		join_room_handler(socket_group_send, payload['room'], payload['user'])


	elif payload['action'] == game_constants.START_GAME:
		start_game_handler(socket_group_send, payload['room'], payload['user'])

	pass

def join_room_handler(socket_group_send, room, user):

	payload = {
		'type': game_constants.UPDATE_PLAYERS,
		'data':{
			'players': get_players_info(room, user),
			}
	}

	socket_group_send(room.group_name, payload)


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

def start_game_handler(socket_group_send, room, user):

	# change room.is_playing to true
	# gather questions
	# tracker for which question we are on

	payload = {
		'type': game_constants.START_GAME,
		'data':{}
	}



	socket_group_send(room.group_name, payload)


	next_run_time = datetime.datetime.now() + datetime.timedelta(seconds=5)

	scheduler.add_job(end_game_handler, args=[socket_group_send, room, user], next_run_time=next_run_time)
	pass

def send_question():

	# update which question the quiz is on

	# send new question

	payload = {
		'type': game_constants.QUESTION_PHASE,
		'question': question
	}

	socket_group_send(room.group_name, payload)

def send_answer():

	# send the answer

	# send the answers each person submitted

	# indicate which answers were correct

	# if its the last question, get ready to end

	payload = {
		'type': game_constants.ANSWER_PHASE,
		'data': {
			'answer': answer,
			'submitted_answers': submitted_answers
		}
		
	}

	socket_group_send(room.group_name, payload)

def retrieve_questions():
	

	return [{
			'question': '1+1',
			'answer': '2'
		},{
			'question': '1+2',
			'answer': '3'
		},{
			'question': '2+3',
			'answer': '3'
		},{
			'question': '5+6',
			'answer': '11'
		},{
			'question': '4+5',
			'answer': '9'
		}]



def end_game_handler(socket_group_send, room, user):
	print('ending game')
	payload = {
		'type': game_constants.END_GAME,
		'data':{
			'players': get_players_info(room, user),
			}
	}

	socket_group_send(room.group_name, payload)
	pass
