from trivia.socket.BaseRoomConsumer import BaseRoomConsumer
from trivia.chat.constants import UPDATE_CHAT
from trivia.game.constants import UPDATE_GAME

class TriviaConsumer(BaseRoomConsumer):
	def message_send(self, event):
		self.helper.self_send(UPDATE_CHAT, event['payload'])
	def game_update(self, event):
		self.helper.self_send(UPDATE_GAME, event['payload'])
