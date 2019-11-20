import functools

def command_router(game_types=[], commands=[]):
	def actual_decorator(func):
		@functools.wraps(func)
		def wrapper(*args, register_command=False, **kwargs):

			if register_command:
				return commands


			if game_types and kwargs['room'].game_type not in game_types:
				return None
			return func(*args, **kwargs)
		return wrapper
	return actual_decorator

