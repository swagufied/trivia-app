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
	# initialize_new_game(room)
	# tracker for which question we are on

	payload = {
		'type': game_constants.START_GAME,
		'data':{}
	}


	# tell everyone in the room that the game is starting
	socket_group_send(room.group_name, payload)

	# start the timer
	next_run_time = datetime.datetime.now() + datetime.timedelta(seconds=3)
	scheduler.add_job(timer, args=[socket_group_send, room, user, 5, 1, send_question], next_run_time=next_run_time)

	next_run_time = datetime.datetime.now() + datetime.timedelta(seconds=5)

	scheduler.add_job(end_game_handler, args=[socket_group_send, room, user], next_run_time=next_run_time)

"""
The timer function for the game

countdown is the current state of the timer
interval is the interval in which the timer update message should be sent
callback will be called once the countdown reaches 0
"""
def timer(socket_group_send, room, user, countdown, interval, callback):
	print(countdown)

	payload = {
		'type': game_constants.UPDATE_TIMER,
		'data': {
			'timer': countdown
		}
	}

	if countdown == 0:
		callback(socket_group_send, room, user)
	else:
		socket_group_send(room.group_name, payload)
		next_run_time = datetime.datetime.now() + datetime.timedelta(seconds=interval)
		scheduler.add_job(timer, args=[socket_group_send, room, user, countdown-interval, interval], next_run_time=next_run_time)


def send_question(socket_group_send, room, user):

	# update which question the quiz is on

	# send new question
	payload = {
		'type': game_constants.QUESTION_PHASE,
		'question': question
	}

	socket_group_send(room.group_name, payload)


	# start the timer
	next_run_time = datetime.datetime.now() + datetime.timedelta(seconds=3)
	scheduler.add_job(timer, args=[socket_group_send, room, user, 10, 1, send_answer], next_run_time=next_run_time)


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
