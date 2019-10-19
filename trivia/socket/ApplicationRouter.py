





class ApplicationRouter:
	command_map = {}
	def __init__(self):

		# iterate through child and compile routing functions
		for prop in dir(self):
			if callable(prop):
				# save all mapping to consumer
				commands[prop] = getattr(self, prop)


	def route_command(self, command, *args, **kwargs):
		commands[command](*args, **kwargs)
