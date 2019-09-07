from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth import get_user_model
from django.conf import settings
import uuid

# Create your models here.
class Room(models.Model):

	TRIVIA = 'TR'
	# TODO: JEOPARDY = 'JE'

	GAME_TYPE_CHOICES = [
		(TRIVIA, 'TRIVIA')
		# TODO: (JEOPARDY, 'JEOPARDY')
	]

	name = models.CharField(max_length = 30, default="All Welcome")
	password = models.CharField(max_length = 30, default="")
	game_type = models.CharField(max_length=2, choices=GAME_TYPE_CHOICES, default=TRIVIA)
	is_playing = models.BooleanField(default=False)
	host = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owned_rooms", null=True, on_delete=models.SET_NULL)


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
	game_data = JSONField(blank=True, default=dict) # this is where questions, answers, and settings are stored


	users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='rooms')

	# for websocket use - designates the group_name used to send messages to room
	@property
	def group_name(self):
		return "room-{}".format(self.id)




class SocketTicketManager(models.Manager):

	def create_ticket(self, user):
		ticket = self.create(user=user)
		return ticket

class SocketTicket(models.Model):

	ticket = models.UUIDField(default=uuid.uuid4, editable=False)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tickets', on_delete=models.CASCADE)
	date_issued = models.DateTimeField(auto_now_add=True)

	objects = SocketTicketManager()
 
