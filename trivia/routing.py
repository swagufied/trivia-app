from . import consumers
from django.conf.urls import url

websocket_urlpatterns = [
	url('', consumers.TriviaConsumer),

    # url(r'^ws/trivia/room/(?P<room_id>[^/]+)/$', consumers.TriviaConsumer),
]