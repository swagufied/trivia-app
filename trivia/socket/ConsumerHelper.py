from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


"""
This class provides the means for a game to manage how socket messages are sent
"""
class ConsumerHelper:

	# user consumer should be the Djanjo channels consumer that has the socket connection
	def __init__(self, consumer):
		self.send_json = consumer.send_json
		self.channel_name = consumer.channel_name
		self.channel_layer = consumer.channel_layer


	# to send to the user socket is connected to
	def self_send(msg_type: str, msg_payload: dict):
		self.send_json({
			'type': msg_type,
			'data': msg_payload 
			})

	# to send to a group group_name
	def group_send(group_name: str, msg_type: str, msg_payload: dict):
		async_to_sync(self.channel_layer.group_send)(
			group_name,
			{
				'type': msg_type,
				'payload': msg_payload
			}
		)

	# to add a member to a group. if the group name doesnt exist, it will automatically be created
	def group_add(channel_name: str, group_name: str):
		async_to_sync(self.channel_layer.group_add)(
			group_name,
			channel_name
		)

	def group_remove(channel_name: str, group_name: str):
		async_to_sync(self.channel_layer.group_discard)(
			group_name,
			channel_name
		)


	