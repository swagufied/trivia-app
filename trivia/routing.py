from game_server.consumer.RoomConsumer import RoomConsumer
from django.conf.urls import url

websocket_urlpatterns = [
	url(r'^test/(?P<room_id>[^/]+)/(?P<ticket>[^/]+)/', RoomConsumer, name="room_consumer"),

    # url(r'^ws/trivia/room/(?P<room_id>[^/]+)/$', consumers.TriviaConsumer),
]