import functools
from game_server.constants import ERROR



def authentication_required(func):
	@functools.wraps(func)
	def wrapper(self, *args, **kwargs):

		if not self.is_authenticated:
			self.self_send(ERROR, {'error_msg': 'Authentication required.'})

		return func(self, *args, **kwargs)
	return wrapper