from .constants import TriviaConstants as game_constants
from ... import scheduler
import datetime
from .temp_functions import retrieve_questions

class Trivia:
	
	def __init__(self, room, socket_group_add, socket_self_send, socket_group_send):
		self.room = room
		self.socket_group_add = socket_group_add
		self.socket_self_send = socket_self_send
		self.socket_group_send = socket_group_send

	"""
	initializes the game

	- updates the game data column of the game
	- pulls the questions that will be answered
	- updates the is_playing bool of room to True

	TODO: get questions from actual source
	"""
	def initialize_game(self):

		# get questions
		questions = retrieve_questions()

		game_data = {
			'questions': [],
			'current_question': None
		}

		for question in questions:
			game_data['questions'].append({
				'question_id': question.get('id') or len(game_data['questions']),
				'question': question['question'],
				'answer': question['answer'],
				'player_answers': {}
				})

		game_data['game_state'] = game_constants.START_GAME

		# update room row
		# room.is_playing = True
		self.room.game_data = game_data
		

	"""
	called when players actually want to start the game.
	the game will run automatically even without user input from this point on

	- sends out game start notification to all players
	- starts timer till first question
	"""
	def start_game(self):

		# initialize the game
		self.initialize_game()

		payload = {
			'type': game_constants.START_GAME,
			'data':{}
		}


		# tell everyone in the room that the game is starting
		self.socket_group_send(self.room.group_name, payload)

		# start the timer countdown till first question
		next_run_time = datetime.datetime.now() + datetime.timedelta(seconds=3)
		scheduler.add_job(self.timer, args=[5, 1, self.send_question], next_run_time=next_run_time)

	"""
	finishes the game up
	- sends out the final scores of each player
	- starts countdown to return to lobby
	"""
	def end_game(self):
		payload = {
			'type': game_constants.END_GAME,
			'data':{
				'players': get_players_info(room, user),
				}
		}

		self.socket_group_send(self.room.group_name, payload)
		pass

	"""
	The timer function for the game

	countdown is the current state of the timer
	interval is the interval in which the timer update message should be sent
	callback will be called once the countdown reaches 0
	"""
	def timer(self, countdown, interval, callback):

		payload = {
			'type': game_constants.UPDATE_TIMER,
			'data': {
				'timer': countdown
			}
		}
		
		self.socket_group_send(self.room.group_name, payload)

		if countdown == 0:
			callback()
		else:
			next_run_time = datetime.datetime.now() + datetime.timedelta(seconds=interval)
			scheduler.add_job(self.timer, args=[countdown-interval, interval, callback], next_run_time=next_run_time)

	"""
	sends the question to each player. starts timer until answer is shown
	"""
	def send_question(self):

		# update the question the game is currently on
		game_data = self.room.game_data
		curr_question_index = game_data['current_question']
		if not curr_question_index:
			game_data['current_question'] = 0
			curr_question_index = 0

		question = {
			'text': game_data['questions'][curr_question_index]['question']
		}

		self.room.game_data = game_data

		# send new question
		payload = {
			'type': game_constants.QUESTION_PHASE,
			'data':{
				'question': question
			}
		}

		self.socket_group_send(self.room.group_name, payload)


		# start the timer
		next_run_time = datetime.datetime.now() + datetime.timedelta(seconds=1)
		scheduler.add_job(self.timer, args=[10, 1, self.send_answer], next_run_time=next_run_time)

	"""
	sends answer to each player
	processes each player's answer
	sends the answers each player provided
	sends if answer was correct or not to each player
	if last question, get ready to end the game
	"""
	def send_answer(self):

		question_index = self.room.game_data['current_question']
		correct_answer = self.room.game_data['questions'][question_index]['answer']

		payload = {
			'type': game_constants.ANSWER_PHASE,
			'data': {
				'correct_answer': correct_answer
			}
		}

		self.room.game_data['current_question'] = question_index + 1

		self.socket_group_send(self.room.group_name, payload)
		
		# start the timer
		next_run_time = datetime.datetime.now() + datetime.timedelta(seconds=1)
		scheduler.add_job(self.timer, args=[5, 1, self.send_question], next_run_time=next_run_time)


	"""
	saves the answer of each player (not in room, in memory for the moment)
	"""
	def process_answer(self, user):


		pass

