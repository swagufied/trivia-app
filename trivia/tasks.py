from __future__ import unicode_literals

from celery import shared_task

from game_server.models import SocketTicket
from game_server import running_games

@shared_task(name='game_server.tasks.invalidate_ticket')
def invalidate_ticket(ticket):
	print("sdsdsdsd")
	SocketTicket.objects.invalidate_ticket(ticket)
	

@shared_task(name='game_server.tasks.update_db')
def update_db(model, data, update_fxn):
	getattr(mode, update_fxn)(data)


@shared_task(name='game_server.tasks.delay_action_task')
def delay_action_task(id, fxn_name, args, kwargs):

	game_manager = running_games.get(id)
	if game_manager:

		for arg in args:
			if isinstance(arg, str):
				cls_str, data = arg.split("||")

				if cls_str == "RowSerializer":
					arg = RowSerializer.load(data)


		getattr(game_manager, fxn_name)(*args, **kwargs)


