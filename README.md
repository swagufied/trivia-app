**Game Server (in development)**

The goal of this project is to provide a framework that will allow anyone to easily program a small game without the hassle of managing sockets, rooms, authentication, etc. Of course, this is just the server. The client is also being designed in a similar fashion and can be found [here](https://github.com/swagufied/trivia-app-client).

**Dependencies**
- Django channels
- Django channels presence
- celery
- redis
- django rest_framework (will be made optional)
- django rest framework simplejwt (will be made optional)

**How to use this?**

This is a django application. Simply put it in your directory (no pip yet) like any other application. Set up celery, django channels, and django channels presence as described in the documents.
- **Checklist**
  - ```
    # project/settings.py

    INSTALLED_APPS = [
      ...
      'channels',
      'channels_presence',
      'celery',
      'game_server', # this application
      ]

    ASGI_APPLICATION = 'project.routing.application'

    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [('127.0.0.1', 6379)],
            },
        },
    }

    CELERY_BROKER_URL = 'redis://localhost:6379'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379'
    CELERY_ACCEPT_CONTENT = ['application/json']
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_BEAT_SCHEDULE = {
        'prune-presence': {
            'task': 'channels_presence.tasks.prune_presence',
            'schedule': timedelta(seconds=60)
        },
        'prune-rooms': {
            'task': 'channels_presence.tasks.prune_rooms',
            'schedule': timedelta(seconds=600)
        }
    }
    ```
  - ```
    # project/celery.py

    import os
    from celery import Celery

    os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

    app = Celery('project')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks()
    ```
**How Does This Work?**

Upon connection, the server will request an authentication message in the following form.
```
{
  'command': "AUTHENTICATE_CONNECTION",
  'room_id': None,
  'data': {
    'ticket': ticket
  }
}
```
Upon success, the following message will be sent to the client
```
{
  'command': "AUTHENTICATE_CONNECTION",
  'room_id': None,
  'data': {
    'is_successful': bool
  }
}
```
Once authenticated, the user can request to join a room.
```
{
  'command': "JOIN_ROOM",
  'room_id': int,
  'data': {
    'password': str
  }
}
```
Upon success, the following message will be sent to the client
```
{
  'command': "JOIN_ROOM",
  'room_id': int,
  'data': {
    'is_successful': bool
  }
}
```

All subsequent messages are received/should be sent to the server in the following form.
```
{
  'command': str,
  'room_id': None or int,
  'data': dict()
}
```
Once a user leaves a room or disconnects, the route with a LEAVE_ROOM command will be run.

This application ensures that each room's connections are grouped into unique users. A single connection per user is not enforced, but an update sent from one connection of a user will update all of that user's connections.


**Getting Started**

  - Router
    - the router is how socket messages will be processed. Simply add the command_router decorator on the desired functions. In the "commands" kwargs, input a list of commands. JOIN_ROOM is called when a user joins a room and LEAVE_ROOM is called when a user leaves.
    ```
    from game_server.router.decorators import command_router
    from game_server.router.BaseRouter import BaseRouter
    from game_server.consumer.constants import JOIN_ROOM, LEAVE_ROOM

    class MyRouter(BaseRouter):

      @command_router(commands=[JOIN_ROOM])
      def join_room(self, data, room=None, user=None, command=None):
        pass

      @command_router(commands=[LEAVE_ROOM])
      def leave_room(self, data, room=None, user=None, command=None):
        pass

      @command_router(commands=["UPDATE_ROOM", "UPDATE_GAME"])
      def update_room(self, data, room=None, user=None, command=None):
        pass
    ```
  - Consumer
    - This is a wrapper for the django channels consumer. All you need to specifiy is a routers property with the associated routers.
    ```
    from game_server.consumer.RoomConsumer import RoomConsumer

    class MyConsumer(RoomConsumer):
      routers = [MyRouter1, MyRouter2]
    ```
  - Connecting the parts
    - in a new application, set up routing.py. Dont forget to set up the project's, routing.py as well according to django channels docs
      ```
      # project/routing.py

      from channels.auth import AuthMiddlewareStack
      from channels.routing import ProtocolTypeRouter, URLRouter
      import app.routing

      application = ProtocolTypeRouter({
          'websocket': AuthMiddlewareStack(
              URLRouter(
                  app.routing.websocket_urlpatterns
              )
          ),
      })
      ```
      ```
      # app/routing.py

      from django.conf.urls import url

      websocket_urlpatterns = [
      	url(r'^mygame/', MyConsumer, name="myconsumer"),
      ]
      ```

**How can I make a game?**

- The games will interact with the client through the routers. When the client sends a message with a specified command, the router should handle how the game or player state changes.
- teams
  - all functions can be imported from "game_server.consumer.consumer_functions"
  - add_user_to_group(room, group_name, user)
    - will add a user to the designated group_name. A group_name could be used as a team or to create groups that receive certain information different from other players
  - remove_user_from_group(room, group_name, user)
    - will remove a user from a group
  - remove_user_from_room(room, user)
    - will kick a user from the room
  - get_group_users(room, group_name) -> list
    - will return a list of users that are a part of the group specified
- send functions
  - user_send(room, user, msg_type, msg_payload)
    - if you want to send a message to a single user
  - group_send(room, group_name, msg_type, msg_payload)
    - if you want to send a message to a group. (see add_user_to_group)
