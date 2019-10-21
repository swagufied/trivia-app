from apscheduler.schedulers.background import BackgroundScheduler
from .chat.ChatRouter import ChatRouter
from .game.trivia.TriviaRouter import TriviaRouter

scheduler = BackgroundScheduler()
scheduler.start()


# initialize a game object for every room that is currently in a game. this is meant as a way to continue games even after a server disconnect
running_games = {}

from channels.layers import get_channel_layer
print('channel layer', get_channel_layer())

routers = [ChatRouter, TriviaRouter]