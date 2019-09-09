from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework.test import force_authenticate

from rest_framework_simplejwt.views import (
	TokenObtainPairView,
	TokenRefreshView,
)
from ..models import SocketTicket, Room


from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator

import uuid


import pytest
from channels.testing import ApplicationCommunicator
from ..consumers import TriviaConsumer
from ..socket.constants import TriviaConsumerConstants as constants


TEST_CHANNEL_LAYERS = {
	'default': {
		'BACKEND': 'channels.layers.InMemoryChannelLayer',
	},
}

@database_sync_to_async
def create_user(username="testuser1", password="testpassword"):
	user = get_user_model().objects.create_user(username=username, password=password)
	return user

@database_sync_to_async
def create_room(name="testroom", password="", game_type=Room.TRIVIA, is_playing=False, host=None):
	user = Room.objects.create_room(name=name, password=password, game_type=game_type, is_playing=is_playing, host=host)
	return user


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_valid_ticket_to_authenticate_connection(settings):
	# Use in-memory channel layers for testing.
	settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

	user = await create_user()
	room = await create_room(host=user)
	socket_ticket = SocketTicket.objects.create_ticket(user)
	assert isinstance(socket_ticket, SocketTicket)

	# Pass session ID in headers to authenticate.
	communicator = WebsocketCommunicator(TriviaConsumer, "/")
		
	connected, subprotocol = await communicator.connect()
	assert connected


	await communicator.send_json_to({
		'type': constants.VALIDATE_CONNECTION,
		'room_id': room.id,
		'data': {
			'ticket': str(socket_ticket.ticket)
		}
	})

	response = await communicator.receive_json_from()

	assert response.get('type') == constants.VALIDATE_CONNECTION
	assert response.get('data')
	assert response['data']['is_successful']

	await communicator.disconnect()

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_invalid_ticket_to_authenticate_connection(settings):
	# Use in-memory channel layers for testing.
	settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

	user = await create_user()
	room = await create_room(host=user)
	socket_ticket = SocketTicket.objects.create_ticket(user)
	assert isinstance(socket_ticket, SocketTicket)


	# Pass session ID in headers to authenticate.
	communicator = WebsocketCommunicator(TriviaConsumer, "/")
		
	connected, subprotocol = await communicator.connect()
	assert connected


	await communicator.send_json_to({
		'type': constants.VALIDATE_CONNECTION,
		'room_id': room.id,
		'data': {
			'ticket': str(uuid.uuid4())
		}
	})

	response = await communicator.receive_json_from()

	assert response.get('type') == constants.VALIDATE_CONNECTION
	assert response.get('data')
	assert not response['data']['is_successful']

	await communicator.disconnect()

# TODO - after celery 
# def test_timed_out_ticket_to_authenticate_connection(self):
	# pass

	# def test_join_no_password_room(self):
	# 	pass

	# def test_join_password_room(self):
	# 	pass

	# def test_join_playing_game_room(self):
		# pass