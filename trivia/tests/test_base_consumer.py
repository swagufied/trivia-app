from django.test import TestCase, RequestFactory, Client

from rest_framework.test import APIRequestFactory, APIClient
from rest_framework.test import force_authenticate

from game_server.models import SocketTicket, Room


from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator

import uuid
from rest_framework.test import APIRequestFactory
from game_server.views import validate_password
from game_server.tasks import invalidate_ticket

import pytest
# from channels.testing import ApplicationCommunicator
from game_server.consumer.RoomConsumer import RoomConsumer
from game_server.consumer.constants import *

from channels.layers import get_channel_layer
from channels.routing import  URLRouter
from django.conf.urls import url
from django.urls import path
from .helpers.model_utils import create_user, create_room

TEST_CHANNEL_LAYERS = {
	'default': {
		'BACKEND': 'channels.layers.InMemoryChannelLayer',
	},
}
from channels.testing import ApplicationCommunicator
# from anime_trivia.routing import application
import uuid
from unittest.mock import patch
from django.test.utils import override_settings

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_consumer_connect(settings):

	user = create_user(username="swagu",password="party123",email="swagu@gmail.com")
	ticket = SocketTicket.objects.create_ticket(user)
	room = create_room(host=user)

	application = URLRouter([url(r"^test/(?P<room_id>\d+)/(?P<ticket>[^/]+)/$", RoomConsumer)])

	communicator = WebsocketCommunicator(application, "/test/{}/{}/".format(room.id, ticket.ticket))
	connected, subprotocol = await communicator.connect()

	assert connected
	assert subprotocol is None

	await communicator.disconnect()

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_ticket_deleted_after_use(settings):

	user = create_user(username="swagu",password="party123",email="swagu@gmail.com")
	ticket = SocketTicket.objects.create_ticket(user)
	room = create_room(host=user)

	application = URLRouter([url(r"^test/(?P<room_id>\d+)/(?P<ticket>[^/]+)/$", RoomConsumer)])

	communicator = WebsocketCommunicator(application, "/test/{}/{}/".format(room.id, ticket.ticket))
	connected, subprotocol = await communicator.connect()
	# Test connection
	assert connected
	assert subprotocol is None

	assert len(SocketTicket.objects.filter(ticket=ticket.ticket)) == 0

	await communicator.disconnect()

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_invalid_ticket(settings):

	user = create_user(username="swagu",password="party123",email="swagu@gmail.com")
	ticket = SocketTicket.objects.create_ticket(user)
	room = create_room(host=user)

	application = URLRouter([url(r"^test/(?P<room_id>\d+)/(?P<ticket>[^/]+)/$", RoomConsumer)])

	invalid_ticket = uuid.uuid4()

	communicator = WebsocketCommunicator(application, "/test/{}/{}/".format(room.id, invalid_ticket))
	connected, subprotocol = await communicator.connect()
	# Test connection
	assert connected
	assert subprotocol is None

	assert len(SocketTicket.objects.filter(ticket=ticket.ticket)) == 1

	await communicator.disconnect()


@override_settings(CELERY_ALWAYS_EAGER=True)
@pytest.mark.django_db(transaction=True)
@patch('game_server.tasks.invalidate_ticket.apply_async')
def test_ticket_invalidation_called(invalidate_ticket, settings):

	user = create_user(username="swagu",password="party123",email="swagu@gmail.com")
	room = create_room(password="sdsd")

	factory = APIRequestFactory()
	request = factory.post('/api/room/{}/validate-password/'.format(room.id), {"password":"sdsd"})


	force_authenticate(request, user=user)
	response = validate_password(request, room_id=room.id)
	assert response.status_code >= 200 and response.status_code < 300
	assert response.data.get('ticket')


	invalidate_ticket.assert_called_with(args=[response.data['ticket']], countdown=30)



@override_settings(CELERY_ALWAYS_EAGER=True)
@pytest.mark.django_db(transaction=True)
def test_ticket_invalidation_task(settings):

	user = create_user(username="swagu",password="party123",email="swagu@gmail.com")
	room = create_room(password="sdsd")

	factory = APIRequestFactory()
	request = factory.post('/api/room/{}/validate-password/'.format(room.id), {"password":"sdsd"})


	force_authenticate(request, user=user)
	response = validate_password(request, room_id=room.id)
	assert response.status_code >= 200 and response.status_code < 300
	assert response.data.get('ticket')

	invalidate_ticket(response.data['ticket'])


	assert len(SocketTicket.objects.filter(ticket=response.data['ticket'])) == 0

		



# test_router_mapping

# test_commands_routed_to_correct_functions