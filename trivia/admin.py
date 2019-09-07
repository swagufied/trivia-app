from django.contrib import admin

# Register your models here.
from .models import Room
import nested_admin

# class AnimeTitleInline(admin.TabularInline):
# 	model = AnimeTitle
# 	extra=1

# class CharPersonRoleInline(admin.TabularInline):
# 	model = CharPersonRole

# class AnimeCharRoleInline(admin.TabularInline):
# 	model = AnimeCharRole
# 	extra=1
# 	inlines = [CharPersonRoleInline,]

# class AnimeRelationInline(admin.TabularInline):
# 	model=Anime.related.through
# 	fk_name = 'related_to'
# 	extra=1



# class AnimeAdmin(admin.ModelAdmin):
# 	inlines = [AnimeTitleInline,  AnimeCharRoleInline, AnimeRelationInline]



class RoomAdmin(nested_admin.NestedModelAdmin):
	pass

admin.site.register(Room, RoomAdmin)

