import functools

def game_type(game_type):
	def actual_decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			print('we here')
			if args[1].game_type != game_type:
				print("game type not match")
				return None
			return func(*args, **kwargs)
		return wrapper
	return actual_decorator