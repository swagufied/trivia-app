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

	# continue the game if server disconnects
	def load_game(self):
		self.send_question()

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

		# initiaize scores
		scores = {}
		for user in self.room.users.all():
			scores[user.username] = 0
		self.scores = scores

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
			'data': {
				'scores': self.scores
			}
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
			'data':{}
		}

		self.socket_group_send(self.room.group_name, payload)

		next_run_time = datetime.datetime.now() + datetime.timedelta(seconds=5)
		scheduler.add_job(self.reset_game, args=[], next_run_time=next_run_time)

	# returns the game back to the lobby state
	def reset_game(self):

		payload = {
			'type': game_constants.RESET,
			'data':{}
		}

		self.socket_group_send(self.room.group_name, payload)


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

		# reset the answer that are received
		self.submitted_answers = {}

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

		# record the answers players have submitted
		player_answers = {}

		for username, submitted_answer in self.submitted_answers.items():
			player_answers[username] = submitted_answer
			if submitted_answer == correct_answer:
				self.scores[username] += 1
		self.room.game_data['questions'][question_index]['player_answers'] = player_answers

		is_finished=False
		if self.room.game_data['current_question']+1 == len(self.room.game_data['questions']):
			is_finished=True
		else:
			# advance the current_question index
			self.room.game_data['current_question'] = question_index + 1


		print('scores', self.scores)

		payload = {
			'type': game_constants.ANSWER_PHASE,
			'data': {
				'correct_answer': correct_answer,
				'points': self.scores,
				'submitted_answers': player_answers,
				'is_finished': is_finished
			}
		}
		
		

		# send the correct answer and submitted answers to everyone
		self.socket_group_send(self.room.group_name, payload)

		

		# if the last question is reached, end the game
		if is_finished:
			next_run_time = datetime.datetime.now() + datetime.timedelta(seconds=1)
			scheduler.add_job(self.timer, args=[5, 1, self.end_game], next_run_time=next_run_time)
		else:
			next_run_time = datetime.datetime.now() + datetime.timedelta(seconds=1)
			scheduler.add_job(self.timer, args=[5, 1, self.send_question], next_run_time=next_run_time)


	"""
	saves the answer of each player (not in room, in memory for the moment)
	"""
	def process_answer(self, username, answer):
		self.submitted_answers[username] = answer

		# meant as a way to acknowledge that an answer was received
		self.socket_self_send({
				'type': game_constants.SUBMIT_ANSWER,
				'data': {
					'answer': answer
				}
			})

