
How to set up your game.

Django channels is used to manage the socket connections. A base consumer is provided to authenticate the server connection and handle connects, disconnects, joining rooms, and leaving rooms. 

{
	'type':
	'room_id':
	'data':
}


- VALIDATE_CONNECTION - 
- JOIN_ROOM - will add the user to the specified room and to the room's socket group. A message will be pinged back indicating if join was successful or not. The password data can be omitted if there is no password required.
	- input: 
	```
	{
		'type': JOIN_ROOM,
		'room_id': int,
		'data': {
			'password': str
		}
	}
	```
	- output:
	```
	{
		'type': JOIN_ROOM,
		'data': {
			'is_successful': bool
		}
	}
	```

- LEAVE_ROOM - will remove the user from the specific room indicated

- disconnect - will remove the user from all rooms that are not currently in-game


To add additional components to the base consumer, you must create routing classes. These classes will be used to handle any messages that have a type that is not specified by the 3 above.

Each of those functions will receive 3 arguments: the room row, user row, helper object, and the data. The room and user are simply the objects you get when you query them. The helper object has functions that allow you to choose how to send messages (see below). The data is the data. 

```
class ChatRouter(BaseRouter):

	def receive_message(room, user, helper, data):
		pass
```
In the router above, when a message is sent with type "receive_message", the base router will route the message to ChatConsumer.receive_message function.

To customize the type input that determines which function processes the message, you can add another function as follows.

```
class ChatRouter(BaseRouter):

	def receive_message():
		pass

	def get_routes(self):
		routes = {
			'RCV_MSG': self.receive_message
		}
		super().get_routes(routes)
```
The get_routes function tells the consumer to route any messages with type "RCV_MSG" to be processed by the "receive_message" function. Do not forget to add super().get_routes(arg) at the end of the function.


The second (and last) part that integrates your game with the server is a consumer to specify how to package the message that will be emitted. Messages are processed exactly the same way as outlined in the Django channels documentations.

Once you have these components setup, just put all the routers in a list called routers in the base directory of the app

app/__init__.py
```
routers = [ChatRouter, GameRouter]
```

The helper object has 4 functions that enable you to add/remove users from socket groups and send messages.

- self_send
- group_send
- group_add
- group_remove