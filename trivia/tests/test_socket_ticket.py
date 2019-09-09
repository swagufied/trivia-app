from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, APIClient
from ..views import SocketTicketView
from rest_framework.test import force_authenticate

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from ..models import SocketTicket


# test socket ticket issue
class SocketTicketTestCase(TestCase):
	def setUp(self):
		self.factory = RequestFactory()
		self.api_factory = APIRequestFactory()

		User = get_user_model()
		self.user = User.objects.create_user(username="testuser1", password="testuser1")

		# obtain token - JWT already tested
		response = APIClient().post('/api/token/', data={"username": "testuser1", "password": "testuser1"})
		self.access_token = response.data['access']
		self.refresh_token = response.data['refresh']

	def test_valid_ticket_issued(self):
		request = self.factory.get('/trivia/socket-ticket')
		force_authenticate(request, user=self.user, token=self.access_token)

		response = SocketTicketView.as_view()(request)

		assert 'ticket' in response.data and isinstance(response.data['ticket'], str)

	def test_valid_ticket_saved_in_db(self):

		request = self.factory.get('/trivia/socket-ticket')
		force_authenticate(request, user=self.user, token=self.access_token)

		response = SocketTicketView.as_view()(request)
		assert 'ticket' in response.data and isinstance(response.data['ticket'], str)

		new_ticket = SocketTicket.objects.get(pk=response.data['ticket'])

		assert new_ticket and isinstance(new_ticket, SocketTicket)

	# TODO - after celery task implemented
	# def test_ticket_invalidated_after_appropriate_time(self):
	# 	pass 

