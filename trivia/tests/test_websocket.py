# from django.test import TestCase, RequestFactory, Client
# from django.contrib.auth import get_user_model
# from rest_framework.test import APIRequestFactory, APIClient
# from rest_framework.test import force_authenticate

# from ..models import SocketTicket, Room


# from channels.db import database_sync_to_async
# from channels.layers import get_channel_layer
# from channels.testing import WebsocketCommunicator

# import uuid


# import pytest
# from channels.testing import ApplicationCommunicator
# from ..consumers import TriviaConsumer
# from ..socket.constants import TriviaConsumerConstants as constants

# from channels.layers import get_channel_layer


# TEST_CHANNEL_LAYERS = {
# 	'default': {
# 		'BACKEND': 'channels.layers.InMemoryChannelLayer',
# 	},
# }

# @database_sync_to_async
# def create_user(username="testuser1", password="testpassword"):
# 	user = get_user_model().objects.create_user(username=username, password=password)
# 	return user

# @database_sync_to_async
# def create_room(name="testroom", password="", game_type=Room.TRIVIA, is_playing=False, host=None):
# 	user = Room.objects.create_room(name=name, password=password, game_type=game_type, is_playing=is_playing, host=host)
# 	return user

# # this validates a socket connection. make sure "test_valid_ticket_to_authenticate_connection" test passes
# async def establish_socket_connection(consumer, route, user, room):

# 	socket_ticket = SocketTicket.objects.create_ticket(user)
# 	communicator = WebsocketCommunicator(TriviaConsumer, "/")
# 	connected, subprotocol = await communicator.connect()
# 	assert connected

# 	await communicator.send_json_to({
# 		'type': constants.VALIDATE_CONNECTION,
# 		'room_id': room.id,
# 		'data': {
# 			'ticket': str(socket_ticket.ticket)
# 		}
# 	})

# 	response = await communicator.receive_json_from()

# 	assert response.get('type') == constants.VALIDATE_CONNECTION
# 	assert response.get('data')
# 	assert response['data']['is_successful']

# 	return communicator


# @pytest.mark.asyncio
# @pytest.mark.django_db(transaction=True)
# async def test_valid_ticket_to_authenticate_connection(settings):
# 	# Use in-memory channel layers for testing.
# 	settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

# 	user = await create_user()
# 	room = await create_room(host=user)
# 	socket_ticket = SocketTicket.objects.create_ticket(user)
# 	assert isinstance(socket_ticket, SocketTicket)

# 	communicator = WebsocketCommunicator(TriviaConsumer, "/")
		
# 	connected, subprotocol = await communicator.connect()
# 	assert connected


# 	await communicator.send_json_to({
# 		'type': constants.VALIDATE_CONNECTION,
# 		'room_id': room.id,
# 		'data': {
# 			'ticket': str(socket_ticket.ticket)
# 		}
# 	})

# 	response = await communicator.receive_json_from()

# 	assert response.get('type') == constants.VALIDATE_CONNECTION
# 	assert response.get('data')
# 	assert response['data']['is_successful']

# 	await communicator.disconnect()

# @pytest.mark.asyncio
# @pytest.mark.django_db(transaction=True)
# async def test_invalid_ticket_to_authenticate_connection(settings):
# 	# Use in-memory channel layers for testing.
# 	settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

# 	user = await create_user()
# 	room = await create_room(host=user)
# 	socket_ticket = SocketTicket.objects.create_ticket(user)
# 	assert isinstance(socket_ticket, SocketTicket)


# 	communicator = WebsocketCommunicator(TriviaConsumer, "/")
		
# 	connected, subprotocol = await communicator.connect()
# 	assert connected


# 	await communicator.send_json_to({
# 		'type': constants.VALIDATE_CONNECTION,
# 		'room_id': room.id,
# 		'data': {
# 			'ticket': str(uuid.uuid4())
# 		}
# 	})

# 	response = await communicator.receive_json_from()

# 	assert response.get('type') == constants.VALIDATE_CONNECTION
# 	assert response.get('data')
# 	assert not response['data']['is_successful']

# 	await communicator.disconnect()

# # TODO - after celery 
# # def test_timed_out_ticket_to_authenticate_connection(self):
# 	# pass

# @pytest.mark.asyncio
# @pytest.mark.django_db(transaction=True)
# async def test_join_valid_room(settings):

# 	settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

# 	# create users and room
# 	host = await create_user()
# 	room = await create_room(host=host)

# 	host_communicator = await establish_socket_connection(TriviaConsumer, "/", host, room)


# 	# host should get 
# 	await host_communicator.send_json_to({
# 		'type': constants.JOIN_ROOM,
# 		'room_id': room.id,
# 		'data': {
# 			'password': None
# 		}
# 	})
# 	host_join_room_response = await host_communicator.receive_json_from()

# 	assert host_join_room_response.get('type') == constants.JOIN_ROOM
# 	assert host_join_room_response.get('data')
# 	assert host_join_room_response['data']['is_successful']

# 	host_chat_update_response = await host_communicator.receive_json_from()
# 	assert host_chat_update_response.get('type') == constants.UPDATE_CHAT
# 	assert host_chat_update_response.get('data')
# 	assert host_chat_update_response['data']['message']

# 	host_room_update_response = await host_communicator.receive_json_from()
# 	assert host_room_update_response.get('type') == constants.UPDATE_ROOM
# 	assert host_room_update_response.get('data')
# 	assert await host_communicator.receive_nothing()

# 	assert host in room.users.all()

# 	await host_communicator.disconnect()


# @pytest.mark.asyncio
# @pytest.mark.django_db(transaction=True)
# async def test_join_invalid_room(settings):

# 	settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

# 	# create users and room
# 	host = await create_user()
# 	room = await create_room(host=host)

# 	host_communicator = await establish_socket_connection(TriviaConsumer, "/", host, room)


# 	# host should get 
# 	await host_communicator.send_json_to({
# 		'type': constants.JOIN_ROOM,
# 		'room_id': room.id + 1,
# 		'data': {
# 			'password': None
# 		}
# 	})
# 	host_join_room_response = await host_communicator.receive_json_from()

# 	assert host_join_room_response.get('error')
# 	assert await host_communicator.receive_nothing()

# 	assert host not in room.users.all()

# 	await host_communicator.disconnect()

# @pytest.mark.asyncio
# @pytest.mark.django_db(transaction=True)
# async def test_current_member_messages_upon_new_member_joining_valid_room(settings):

# 	settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

# 	# create users and room
# 	host = await create_user()
# 	member = await create_user(username="member")
# 	room = await create_room(host=host)


# 	host_communicator = await establish_socket_connection(TriviaConsumer, "/", host, room)
# 	member_communicator = await establish_socket_connection(TriviaConsumer, "/", member, room)



# 	# host should get 
# 	await host_communicator.send_json_to({
# 		'type': constants.JOIN_ROOM,
# 		'room_id': room.id,
# 		'data': {
# 			'password': None
# 		}
# 	})
# 	host_join_room_response = await host_communicator.receive_json_from()

# 	assert host_join_room_response.get('type') == constants.JOIN_ROOM
# 	assert host_join_room_response.get('data')
# 	assert host_join_room_response['data']['is_successful']

# 	host_chat_update_response = await host_communicator.receive_json_from()
# 	assert host_chat_update_response.get('type') == constants.UPDATE_CHAT
# 	assert host_chat_update_response.get('data')
# 	assert host_chat_update_response['data']['message']

# 	host_room_update_response = await host_communicator.receive_json_from()
# 	assert host_room_update_response.get('type') == constants.UPDATE_ROOM
# 	assert host_room_update_response.get('data')
# 	assert await host_communicator.receive_nothing()

# 	assert host in room.users.all()
	

# 	# member should get 
# 	await member_communicator.send_json_to({
# 		'type': constants.JOIN_ROOM,
# 		'room_id': room.id,
# 		'data': {
# 			'password': None
# 		}
# 	})
# 	member_join_room_response = await member_communicator.receive_json_from()

# 	assert member_join_room_response.get('type') == constants.JOIN_ROOM
# 	assert member_join_room_response.get('data')
# 	assert member_join_room_response['data']['is_successful']

# 	member_chat_update_response = await member_communicator.receive_json_from()
# 	assert member_chat_update_response.get('type') == constants.UPDATE_CHAT
# 	assert member_chat_update_response.get('data')
# 	assert member_chat_update_response['data']['message']

# 	member_room_update_response = await member_communicator.receive_json_from()
# 	assert member_room_update_response.get('type') == constants.UPDATE_ROOM
# 	assert member_room_update_response.get('data')
# 	assert await member_communicator.receive_nothing()

# 	assert member in room.users.all()

# 	# make sure everyone is notified
# 	room_update_chat_response = await host_communicator.receive_json_from()
# 	assert room_update_chat_response.get('type') == constants.UPDATE_CHAT
# 	assert room_update_chat_response.get('data')
# 	assert room_update_chat_response['data']['message']

# 	room_room_update_response = await host_communicator.receive_json_from()
# 	assert room_room_update_response.get('type') == constants.UPDATE_ROOM
# 	assert room_room_update_response.get('data')
# 	assert await host_communicator.receive_nothing()


# 	await host_communicator.disconnect()
# 	await member_communicator.disconnect()


# @pytest.mark.asyncio
# @pytest.mark.django_db(transaction=True)
# async def test_joining_room_with_valid_password(settings):
# 	settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

# 	# create users and room
# 	host = await create_user()
# 	room = await create_room(host=host, password="1")

# 	host_communicator = await establish_socket_connection(TriviaConsumer, "/", host, room)


# 	# host should get 
# 	await host_communicator.send_json_to({
# 		'type': constants.JOIN_ROOM,
# 		'room_id': room.id,
# 		'data': {
# 			'password': "1"
# 		}
# 	})
# 	host_join_room_response = await host_communicator.receive_json_from()

# 	assert host_join_room_response.get('type') == constants.JOIN_ROOM
# 	assert host_join_room_response.get('data')
# 	assert host_join_room_response['data']['is_successful']

# 	host_chat_update_response = await host_communicator.receive_json_from()
# 	assert host_chat_update_response.get('type') == constants.UPDATE_CHAT
# 	assert host_chat_update_response.get('data')
# 	assert host_chat_update_response['data']['message']

# 	host_room_update_response = await host_communicator.receive_json_from()
# 	assert host_room_update_response.get('type') == constants.UPDATE_ROOM
# 	assert host_room_update_response.get('data')
# 	assert await host_communicator.receive_nothing()

# 	assert host in room.users.all()

# 	await host_communicator.disconnect()


# @pytest.mark.asyncio
# @pytest.mark.django_db(transaction=True)
# async def test_joining_room_with_invalid_password(settings):
# 	settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

# 	# create users and room
# 	host = await create_user()
# 	room = await create_room(host=host, password="1")

# 	host_communicator = await establish_socket_connection(TriviaConsumer, "/", host, room)


# 	# host should get 
# 	await host_communicator.send_json_to({
# 		'type': constants.JOIN_ROOM,
# 		'room_id': room.id,
# 		'data': {
# 			'password': "3"
# 		}
# 	})
# 	host_join_room_response = await host_communicator.receive_json_from()

# 	assert host_join_room_response.get('error')
# 	assert await host_communicator.receive_nothing()

# 	assert host not in room.users.all()

# 	await host_communicator.disconnect()


# @pytest.mark.asyncio
# @pytest.mark.django_db(transaction=True)
# async def test_current_member_messages_upon_new_member_joining_room_with_invalid_password(settings):

# 	settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

# 	# create users and room
# 	host = await create_user()
# 	member = await create_user(username="member")
# 	room = await create_room(host=host, password="1")

# 	# preset room with a member
# 	room.users.add(host)


# 	host_communicator = await establish_socket_connection(TriviaConsumer, "/", host, room)
# 	member_communicator = await establish_socket_connection(TriviaConsumer, "/", member, room)


# 	# host should get 
# 	await host_communicator.send_json_to({
# 		'type': constants.JOIN_ROOM,
# 		'room_id': room.id,
# 		'data': {
# 			'password': "1"
# 		}
# 	})
# 	host_join_room_response = await host_communicator.receive_json_from()

# 	while True:
# 		response = await host_communicator.receive_json_from()
# 		if await host_communicator.receive_nothing():
# 			break

# 	assert host in room.users.all()
	

# 	# member should get 
# 	await member_communicator.send_json_to({
# 		'type': constants.JOIN_ROOM,
# 		'room_id': room.id,
# 		'data': {
# 			'password': None
# 		}
# 	})
# 	member_join_room_response = await member_communicator.receive_json_from()

# 	assert member_join_room_response.get('error')
# 	assert await member_communicator.receive_nothing()
# 	assert await host_communicator.receive_nothing()

# 	assert member not in room.users.all()

# 	await host_communicator.disconnect()
# 	await member_communicator.disconnect()

# @pytest.mark.asyncio
# @pytest.mark.django_db(transaction=True)
# async def test_leave_room_upon_disconnect(settings):
# 	settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

# 	# create users and room
# 	host = await create_user()
# 	room = await create_room(host=host)

# 	host_communicator = await establish_socket_connection(TriviaConsumer, "/", host, room)


# 	# host should get 
# 	await host_communicator.send_json_to({
# 		'type': constants.JOIN_ROOM,
# 		'room_id': room.id,
# 		'data': {
# 			'password': None
# 		}
# 	})
# 	while True:
# 		response = await host_communicator.receive_json_from()
# 		if await host_communicator.receive_nothing():
# 			break

	
# 	await host_communicator.disconnect()

# 	assert host not in room.users.all()


# @pytest.mark.asyncio
# @pytest.mark.django_db(transaction=True)
# async def test_leave_room(settings):
# 	settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

# 	# create users and room
# 	host = await create_user()
# 	room = await create_room(host=host)

# 	host_communicator = await establish_socket_connection(TriviaConsumer, "/", host, room)


# 	# host should get 
# 	await host_communicator.send_json_to({
# 		'type': constants.JOIN_ROOM,
# 		'room_id': room.id,
# 		'data': {
# 			'password': None
# 		}
# 	})
	
# 	while True:
# 		response = await host_communicator.receive_json_from()
# 		if await host_communicator.receive_nothing():
# 			break

# 	await host_communicator.send_json_to({
# 		'type': constants.LEAVE_ROOM,
# 		'room_id': room.id,
# 		'data': {}
# 	})

# 	response = await host_communicator.receive_json_from()
# 	assert response.get('type') == constants.LEAVE_ROOM
# 	assert response.get('data')
# 	assert response['data']['is_successful']

# 	assert host not in room.users.all()
	
# 	await host_communicator.disconnect()

# @pytest.mark.asyncio
# @pytest.mark.django_db(transaction=True)
# async def test_leave_invalid_room(settings):
# 	settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

# 	# create users and room
# 	host = await create_user()
# 	room = await create_room(host=host)

# 	host_communicator = await establish_socket_connection(TriviaConsumer, "/", host, room)


# 	# host should get 
# 	await host_communicator.send_json_to({
# 		'type': constants.JOIN_ROOM,
# 		'room_id': room.id,
# 		'data': {
# 			'password': None
# 		}
# 	})
	
# 	while True:
# 		response = await host_communicator.receive_json_from()
# 		if await host_communicator.receive_nothing():
# 			break

# 	await host_communicator.send_json_to({
# 		'type': constants.LEAVE_ROOM,
# 		'room_id': room.id,
# 		'data': {}
# 	})

# 	response = await host_communicator.receive_json_from()
# 	assert response.get('type') == constants.LEAVE_ROOM
# 	assert response.get('data')
# 	assert response['data']['is_successful']

# 	assert host not in room.users.all()
	
# 	await host_communicator.disconnect()

	
# # test_leave_all_rooms_on_disconnect
# # test_stay_in_rooms_that_are_ingame

# # test_send_valid_message
# # test_send_empty_message
# # test_all_member_receive_message

# # test_host_game_start
# # test_nonhost_game_start