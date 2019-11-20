from django.contrib import admin
from game_server.models import Room
import nested_admin


class RoomAdmin(nested_admin.NestedModelAdmin):
	pass

admin.site.register(Room, RoomAdmin)

