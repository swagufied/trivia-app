from ..models import Room
# from ...anime_database.celery import app

def send_email(fun):
    @wraps(fun)
    def outer(self, *args, **kwargs):
        print('decorated and task is {0!r}'.format(self))
        return fun(self, *args, **kwargs)

    return outer


class StandardTrivia:


	def update_state(room, state):

		room.data['game_state'] = state
		payload = {}
		if state == 'GAME_START':

			# retrieve questions
			questions = StandardTrivia.get_questions()
			room.data['questions'] = questions

			payload = {
				'type': 'UPDATE_GAME',
				'data': {
					'gameState': 'START_COUNTDOWN',
					'timer': 10
				}
			}

		room.save()
		return payload

	def get_questions():
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

	def pre_countdown(consumer, seconds):


		# after x seconds, send question


		# to test, send ping every 3s

		StandardTrivia.question.apply_async(args=[consumer], countdown=3)

	
	def question(consumer):

		# after x seconds, send answer

		TriviaConsumer.timed_send.apply_sync()

		# change state of game to QUESTION
		# any answers submitted should be notified to other players

	def answer(consumer):

		# after x seconds, send next question

		# change gameSatate to ANSWER
		# send out everyone's answers
		# send out updated points
		# send out who got answers right

		pass

