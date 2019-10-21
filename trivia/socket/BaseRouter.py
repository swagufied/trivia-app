from .consumer_constants import JOIN_ROOM, LEAVE_ROOM


class BaseRouter:

	def get_routes(self, routes={}):

		modified = False
		if len(list(routes.keys())) > 0:
			modified = True

		# iterate through child and compile routing functions
		for prop in dir(self):

			if prop[0] != "_" and prop != "get_routes" and callable(getattr(self,prop)):
				# save all mapping to consumer

				# if route is join room
				if getattr(self, prop).__name__ == "join_room" and (not modified or JOIN_ROOM not in routes):
					routes[JOIN_ROOM] = getattr(self, prop)

				# if route is leave room
				elif getattr(self, prop).__name__ == "leave_room" and (not modified or LEAVE_ROOM not in routes):
					routes[LEAVE_ROOM] = getattr(self, prop)

				else:

					routes[getattr(self, prop).__name__] = getattr(self, prop)

		return routes
