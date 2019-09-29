**Game Server (in development)**

The goal of this project is to provide a framework that will allow anyone to easily program a small game without the hassle of managing socket, rooms, authentication, etc. Of course, this is just the server. The client is also being designed in a similar fashion and can be found [here](https://github.com/swagufied/trivia-app-client). A simple chat system is built in as well.

**How to use this?**

Currently, the project is not useable as it isn't finished and not fully tested. It will eventually be a Django application will require a User table for user authentication. Otherwise the application should stand on its own.

**How can I insert a game?**

Each game will need a function that can receive the incoming socket and socket send functions. An example can be seen below.
```
def payload_handler(group_add, socket_self_send, socket_group_send, payload):
  pass
```
- group_add would be a way to add users to a designated group which can be used to create teams.
- socket_self_send would be a way to send socket messages to the user from which the socket message originated
- socket_group_send would be a way to send socket messages to designated groups that were created by group_add
- payload would be the data itself

**Some Notes**
- All timed events are currently planned to be managed by [apscheduler](https://apscheduler.readthedocs.io/en/latest/).
- Each game currently receives one row in the database. The data would be stored as a JSON object. This means that currently, the server cannot handle games that require large amounts of data.

**When will it be finished?**

This project is running concurrently with the main project for which this framework was designed. Features will be added as they are tested in the main project.

**Future planned improvements**
- Configure how data is stored to allot a greater amount of data space per game.
- Experiment with methods to handle more rapid transmissions of data, possibly by converting messages into binary representations.
- Allow chat integrations into the games themselves so that they can be customized based on the game (e.g. team messages)
