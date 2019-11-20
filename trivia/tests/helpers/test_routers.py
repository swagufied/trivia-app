
GT1 = "TR"
GT2 = "JE"

JOIN_ROOM = "JOIN_ROOM"
LEAVE_ROOM = "LEAVE_ROOM"
UPDATE_ROOM = "UPDATE_ROOM"



class OneGameRouter(BaseRouter):



	@game_type(game_types=[GT1], commands=[JOIN_ROOM])
	def join_room(self, room, user, helper):
		pass

	@game_type(game_types=[GT1], commands=[JOIN_ROOM])
	def join_room2(self, room, user, helper):


	@game_type(game_types=[GT1], commands=[LEAVE_ROOM])
	def leave_room(self, room, user, helper):
		pass

	@game_type(game_types=[GT1], commands=[UPDATE_ROOM])
	def update_room(self, room, user, helper):
		pass
