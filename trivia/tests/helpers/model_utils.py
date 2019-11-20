from django.contrib.auth import get_user_model
import random
import string
from game_server.models import *

def create_user(username:str=None, password:str=None, email:str=None):

	if username is None:
		username = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)])

	if password is None:
		password = text = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])

	if email is None:
		email = text = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(8)]) + '@gamil.com'
	
	return get_user_model().objects.create_user(username=username, password=password, email=email)


def create_room(name:str=None, password:str=None, game_type:int=None, is_playing:bool=None, host=None):

	if name is None:
		name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])

	if password is None:
		password = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])
	
	if game_type is None:
		game_type = 1

	if is_playing is None:
		is_playing = False

	if host is None:
		host = get_user_model().objects.all()[0]

	return Room.objects.create_room(name=name, password=password, game_type=game_type, is_playing=is_playing, host=host)
