from game_server.consumer.constants import JOIN_ROOM, LEAVE_ROOM


class BaseRouter:



	def get_routes(self):
		routes={}
		modified = False	
		if len(list(routes.keys())) > 0:
			modified = True

		# iterate through child and compile routing functions
		for prop in dir(self):

			if prop[0] != "_" and prop != "get_routes" and callable(getattr(self,prop)):

				try:
					commands = getattr(self, prop)(register_command=True)
				except Exception as e:
					continue

				for command in commands:

					if command in routes:
						routes[command].append(getattr(self, prop))
					else:

						routes[command] = [getattr(self, prop)]

		return routes
