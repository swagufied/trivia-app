from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from channels_presence.models import Room as Group, Presence


"""
CHANNEL NAME
"""

def prepend_room_group_name_to_group_name(room, group_name):
	return "{}-group-{}".format(room.group_name, group_name)

def get_user_group_name(room, user):
	return "{}-user-{}".format(room.group_name, user.id)

"""
SEND FUNCTIONS
"""
def user_send(room, user, msg_type:str, msg_payload: dict):

	async_to_sync(get_channel_layer().group_send)(
		get_user_group_name(room, user),
		{
			# 'type': msg_type,
			'type': 'message.send',
			'payload': {
					'type': msg_type,
					'data': msg_payload
				}
		}
	)



# to send to a group group_name
def group_send(room, group_name: str, msg_type: str, msg_payload: dict):

	# if group_name is None, send message to all people in the room
	if group_name is None:
		group_name = room.group_name
	else:
		group_name = prepend_room_group_name_to_group_name(room, group_name)


	async_to_sync(get_channel_layer().group_send)(
		group_name,
		{
			# 'type': msg_type,
			'type': 'message.send',
			'payload': {
					'type': msg_type,
					'data': msg_payload
				}
		}
	)


"""
GROUP CREATION/DESTRUCTION
"""

# adds users to socket group. should be used to organize teams
def add_channel_to_group(group_name, channel_name, user):
	Group.objects.add(group_name, channel_name, user)

def add_user_to_group(room, group_name, user, add_prefix=True):

	if add_prefix:
		group_name = prepend_room_group_name_to_group_name(room, group_name)

	user_channels = Presence.objects.filter(room__channel_name=room.group_name, user=user).all()

	for user_channel in user_channels:
		add_channel_name_to_group(group_name, user_channel.channel_name, user)

# removes users from socket group. should be used to dissociate teams
def remove_channel_from_group(group_name, channel_name):
	Group.objects.remove(group_name, channel_name)

def remove_user_from_group(room, group_name, user):

	if add_prefix:
		group_name = prepend_room_group_name_to_group_name(room, group_name)

	user_channels = Presence.objects.filter(room__channel_name=room.group_name, user=user).all()

	for user_channel in user_channels:
		remove_channel_name_from_group(group_name, user_channel.channel_name)

# removes all connections associated with user - meant to be used when user leaves room or is kicked from room
def remove_channel_from_room(room, channel_name):
	user_channels = Presence.objects.filter(room__channel_name__beginswith=room.group_name, channel_name=channel_name).all()

	for channel in user_channels:
		remove_channel_name_from_group(channel.room.channel_name, channel.channel_name)


def remove_user_from_room(room, user):
	user_channels = Presence.objects.filter(room__channel_name__beginswith=room.group_name, user=user).all()

	for channel in user_channels:
		remove_channel_name_from_group(channel.room.channel_name, channel.channel_name)


def get_group_users(room, group_name, add_prefix=True):

	if add_prefix:
		group_name = prepend_room_group_name_to_group_name(room, group_name)

	group = Group.objects.get(channel_name=group_name)
	return group.get_users()