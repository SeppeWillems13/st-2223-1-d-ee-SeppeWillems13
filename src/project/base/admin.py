from django.contrib import admin

# Register your models here.

from .models import Room, User, Game, Player

admin.site.register(User)
admin.site.register(Room)
admin.site.register(Game)
admin.site.register(Player)
