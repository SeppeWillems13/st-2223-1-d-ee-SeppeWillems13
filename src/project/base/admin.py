from django.contrib import admin

from .models import Room, User, Game, Player, Round, Result

# Register your models here.

admin.site.register(User)
admin.site.register(Room)
admin.site.register(Game)
admin.site.register(Player)
admin.site.register(Round)
admin.site.register(Result)
