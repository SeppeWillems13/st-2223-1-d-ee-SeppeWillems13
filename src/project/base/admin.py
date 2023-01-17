from django.contrib import admin

from .models import Room, User, Game, Player

# Register your models here.

admin.site.register(User)
admin.site.register(Room)
admin.site.register(Game)
admin.site.register(Player)
