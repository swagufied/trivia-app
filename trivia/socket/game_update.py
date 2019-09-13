from ..game.trivia.payload_handler import trivia_payload_handler
from ..models import Room 
# send an answer
# start game



# this function will send the socket payload to the right game. Each game should have a function that then handles the payload contents and returns the necessary info to the socket


def game_update_payload(command, group_add, socket_self_send, socket_group_send, data):

	commands = {
		Room.TRIVIA: trivia_payload_handler
	}

	return commands[command](group_add, socket_self_send, socket_group_send, data)

