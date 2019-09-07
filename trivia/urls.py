# chat/urls.py
from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    url(r'^room/(?P<room_id>[^/]+)/$', views.RoomView.as_view(), name='room'),
    path('token-verify/', views.TokenView.as_view(), name='token_verify'), # get rid of
    path('socket-ticket', views.SocketTicketView.as_view(), name='socket-ticket')
]