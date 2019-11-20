from rest_framework import routers
from django.conf.urls import url
from django.urls import include

from game_server.views import RoomView, validate_password, SocketTicketView



urlpatterns = [
	url(r'^socket-ticket/$', SocketTicketView.as_view(), name='socket-ticket'),
	url(r'^room/(?P<room_id>[^/]+)/$', RoomView.as_view(), name='room'),
	url(r'^room/(?P<room_id>[^/]+)/validate-password', validate_password, name='validate-password'),
]

