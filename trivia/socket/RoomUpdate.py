class RoomUpdate:

	# players must be a list of user objs
	def player_list(players: list):
		player_list = []
		for player in players:
			player_list.append({
					'username': player.username
				})

		return player_list

	def is_host(boolean):
		return boolean