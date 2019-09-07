

def get_user_from_socket_ticket(ticket):

	ticket_row = SocketTicket.object.filter(pk=ticket)

	# make sure ticket time is still valid
	if ticket_row: # and utcnow - ticket_row.date <= 5min:
		return ticket_row.user

	return None
